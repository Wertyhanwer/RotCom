"""Запись событий чата: событие в Mongo + превью чата в Postgres.

Две базы нельзя обновить одной транзакцией, поэтому событие в Mongo — источник истины, а
last_message/last_event_at в Postgres — производная проекция от него. Документ события
записывается вместе с полем outbox (что нужно применить к Postgres), после успешного
обновления превью поле outbox удаляется. Если процесс упал или Postgres был недоступен между
этими шагами, документ остаётся с outbox, и фоновая досинхронизация (reconcile_pending_events)
применяет его позже. Так это работает как transactional outbox, где outbox — сама коллекция событий.

Применение превью идемпотентно и монотонно: UPDATE срабатывает, только если событие не старше
текущего превью, поэтому повторное или запоздалое применение не затирает более свежее.
"""
import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone

from pymongo.asynchronous.database import AsyncDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.private_chat import PrivateChat
from db.repository.chat_event_repository import ChatEventRepository
from db.repository.private_chat_repository import PrivateChatRepository
from schemas.chat_event import BaseEvent

logger = logging.getLogger("messenger.chat_events")

# как часто искать недоприменённые события и сколько ждать, прежде чем считать их «зависшими»
RECONCILE_INTERVAL = float(os.getenv("CHAT_EVENT_RECONCILE_INTERVAL", "30"))
RECONCILE_GRACE = float(os.getenv("CHAT_EVENT_RECONCILE_GRACE", "10"))


async def save_chat_event(session: AsyncSession, mongo_db: AsyncDatabase,
                          chat: PrivateChat, sender_id: int, event: BaseEvent) -> dict:
    """Сохраняет событие. Ошибка записи в Mongo — событие не сохранено (исключение).
    Ошибка обновления превью в Postgres событие не теряет: его досинхронизирует фоновая задача."""
    document = event.model_dump(mode="json", exclude={"to_user_id"})
    document |= {
        "chat_id": chat.id_,
        "sender_id": sender_id,
        "created_at": datetime.now(timezone.utc),
        "outbox": {"preview": event.preview()},
    }

    event_rep = ChatEventRepository(mongo_db)
    await event_rep.create(document)

    try:
        await apply_preview(session, event_rep, document)
    except Exception:
        logger.exception(f"Preview update deferred to reconciliation {{event_id: {document['_id']}}}")

    document.pop("outbox", None)
    return document


async def apply_preview(session: AsyncSession, event_rep: ChatEventRepository, document: dict):
    """Применяет outbox документа к Postgres и снимает отметку outbox в Mongo."""
    created_at = document["created_at"].astimezone(timezone.utc).replace(tzinfo=None)
    try:
        await PrivateChatRepository(session).update_last_event(
            document["chat_id"], document["outbox"]["preview"], created_at)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    await event_rep.mark_projected(document["_id"])


async def reconcile_pending_events(session_factory, mongo_db: AsyncDatabase, limit: int = 100) -> int:
    """Один проход досинхронизации: применяет превью событий, у которых осталось поле outbox."""
    event_rep = ChatEventRepository(mongo_db)
    older_than = datetime.now(timezone.utc) - timedelta(seconds=RECONCILE_GRACE)
    pending = await event_rep.find_pending(older_than, limit)
    applied = 0
    for document in pending:
        try:
            async with session_factory() as session:
                await apply_preview(session, event_rep, document)
            applied += 1
        except Exception:
            logger.exception(f"Reconciliation failed {{event_id: {document['_id']}}}")
    if applied:
        logger.warning(f"Reconciled chat previews for {applied} event(s)")
    return applied


async def run_reconciler(session_factory, mongo_db: AsyncDatabase):
    """Фоновая задача api: периодически досинхронизирует превью. Безопасно запускать в
    нескольких процессах одновременно — применение идемпотентно."""
    while True:
        try:
            await reconcile_pending_events(session_factory, mongo_db)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Reconciler pass failed")
        await asyncio.sleep(RECONCILE_INTERVAL)
