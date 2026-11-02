import logging
from datetime import datetime, timezone

from pymongo.asynchronous.database import AsyncDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.private_chat import PrivateChat
from db.repository.chat_event_repository import ChatEventRepository
from db.repository.private_chat_repository import PrivateChatRepository
from schemas.chat_event import BaseEvent

logger = logging.getLogger("messenger.chat_events")


async def save_chat_event(session: AsyncSession, mongo_db: AsyncDatabase,
                          chat: PrivateChat, sender_id: int, event: BaseEvent) -> dict:
    """Пишет событие в Mongo и обновляет превью чата в Postgres так, чтобы при ошибке
    в любой из баз не осталось половины записи:

    1. UPDATE private_chats в открытой транзакции Postgres (не коммитим)
    2. insert в Mongo — упал → rollback Postgres
    3. commit Postgres — упал → удаляем документ из Mongo (компенсация)
    """
    document = event.model_dump(mode="json", exclude={"to_user_id"})
    document |= {
        "chat_id": chat.id_,
        "sender_id": sender_id,
        "created_at": datetime.now(timezone.utc),
    }

    chat_rep = PrivateChatRepository(session)
    event_rep = ChatEventRepository(mongo_db)

    try:
        await chat_rep.update_last_event(chat.id_, event.preview())
        await event_rep.create(document)
    except Exception:
        await session.rollback()
        raise

    # TODO: если процесс умрёт здесь (kill, рестарт контейнера) — событие в Mongo останется, а last_event/last_message
    #  в чате отстанут. Закрыть через очередь (outbox / событие chat_event_created)
    try:
        await session.commit()
    except Exception:
        try:
            await event_rep.delete_by_id(document["_id"])
        except Exception:
            logger.critical(f"Compensation failed, orphan chat event in Mongo: {document['_id']}")
        raise

    return document
