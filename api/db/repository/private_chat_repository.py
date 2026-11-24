import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_, case
from sqlalchemy.exc import IntegrityError

from db.models.private_chat import PrivateChat
from db.models.user import User
from db.exceptions import DatabaseError

class PrivateChatRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._logger = logging.getLogger("messenger.db")

    async def create(self, user_a: User , user_b: User) -> PrivateChat:
        """Создаёт чат пары или возвращает существующий.

        Между get_by_users() и create() другой запрос мог уже создать чат этой пары
        (одновременные первые сообщения). Уникальный индекс uq_private_chats_users не даёт
        вставить дубликат, а IntegrityError здесь означает «чат уже есть» — забираем его.
        """
        self._logger.info(f"Private chat create request {{user_a: {user_a.id_}, user_b: {user_b.id_}}}")
        user_id_1 = min(user_a.id_, user_b.id_)
        user_id_2 = max(user_a.id_, user_b.id_)
        try:
            chat = PrivateChat(user1_id=user_id_1, user2_id=user_id_2)
            self._session.add(chat)
            await self._session.commit()
            await self._session.refresh(chat)
            return chat
        except IntegrityError:
            await self._session.rollback()
            existing = await self._get_by_user_ids(user_id_1, user_id_2)
            if existing is not None:
                self._logger.info(f"Private chat already created concurrently {{chat_id: {existing.id_}}}")
                return existing
            raise DatabaseError(f"Error at creating private chat {{users: {user_id_1}/{user_id_2}}}")
        except Exception as e:
            self._logger.error(
                f"Error at creating private chat {{users: {user_id_1}/{user_id_2}}}: {e}")
            raise DatabaseError(
                f"Error at creating private chat {{users: {user_id_1}/{user_id_2}}}: {e}") from e

    async def _get_by_user_ids(self, user_id_1: int, user_id_2: int) -> PrivateChat | None:
        result = await self._session.execute(select(PrivateChat).where(
            PrivateChat.user1_id == user_id_1,
            PrivateChat.user2_id == user_id_2,
        ))
        return result.scalar_one_or_none()


    async def get_by_users(self, user_a: User , user_b: User) -> PrivateChat | None:
        self._logger.info(f"Private chat request {{user_a: {user_a}, user_b: {user_b}}}")
        try:
            private_chat_request = select(PrivateChat).where(
                PrivateChat.user1_id == min(user_a.id_, user_b.id_),
                PrivateChat.user2_id == max(user_a.id_, user_b.id_)
            )
            private_chat = await self._session.execute(private_chat_request)
            return private_chat.scalar_one_or_none()
        except Exception as e:
            self._logger.error(
                f"Error at requesting private chat {{user_a: {user_a}, user_b: {user_b}}}: {e}")
            raise DatabaseError(
                f"Error at requesting private chat {{user_a: {user_a}, user_b: {user_b}}}: {e}") from e

    async def get_all_by_user(self, user_id: int, limit: int=50, offset: int=0) -> list:
        self._logger.info(f"Chats requests by user_id: {{user_id: {user_id}, limit: {limit}, offset: {offset}}}")
        try:
            private_chat_request = select(PrivateChat, User).join(
                User,
                User.id_ == case((PrivateChat.user1_id == user_id, PrivateChat.user2_id), else_=PrivateChat.user1_id)
            ).where(
                or_(PrivateChat.user1_id == user_id, PrivateChat.user2_id == user_id)
            ).order_by(PrivateChat.last_event_at.desc()).limit(limit).offset(offset)
            private_chat_with_user_data = await self._session.execute(private_chat_request)
            return private_chat_with_user_data.all()
        except Exception as e:
            self._logger.error(
                f"Error at requesting private chats by user_id {{user_id: {user_id}, limit: {limit}, offset: {offset}}}: {e}")
            raise DatabaseError(
                f"Error at requesting private chats by user_id {{user_id: {user_id}, limit: {limit}, offset: {offset}}}") from e

    async def get_by_id_for_user(self, chat_id: int, user_id: int) -> PrivateChat | None:
        """Чат по id, только если user_id его участник — иначе None."""
        self._logger.info(f"Private chat request {{chat_id: {chat_id}, user_id: {user_id}}}")
        try:
            private_chat_request = select(PrivateChat).where(
                PrivateChat.id_ == chat_id,
                or_(PrivateChat.user1_id == user_id, PrivateChat.user2_id == user_id)
            )
            private_chat = await self._session.execute(private_chat_request)
            return private_chat.scalar_one_or_none()
        except Exception as e:
            self._logger.error(f"Error at requesting private chat {{chat_id: {chat_id}, user_id: {user_id}}}: {e}")
            raise DatabaseError(f"Error at requesting private chat {{chat_id: {chat_id}, user_id: {user_id}}}") from e

    async def update_last_event(self, chat_id: int, last_message: str):
        """Без commit — коммитит вызывающий (services/chat_events.py), чтобы откатить при ошибке записи в Mongo."""
        self._logger.info(f"Private chat last event update request {{chat_id: {chat_id}}}")
        try:
            await self._session.execute(
                update(PrivateChat)
                .where(PrivateChat.id_ == chat_id)
                .values(last_event_at=func.now(), last_message=last_message)
            )
        except Exception as e:
            self._logger.error(f"Error at updating private chat last event {{chat_id: {chat_id}}}: {e}")
            raise DatabaseError(f"Error at updating private chat last event {{chat_id: {chat_id}}}") from e




