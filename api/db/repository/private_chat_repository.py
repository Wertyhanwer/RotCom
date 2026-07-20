import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, case

from db.models.private_chat import PrivateChat
from db.models.user import User
from db.exceptions import DatabaseError

class PrivateChatRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._logger = logging.getLogger("messenger.db")

    async def create(self, user_a: User , user_b: User) -> PrivateChat:
        self._logger.info(f"Private chat create request {{user_a: {user_a}, user_b: {user_b}}}")
        user_id_1 = min(user_a.id_, user_b.id_)
        user_id_2 = max(user_a.id_, user_b.id_)
        try:
            chat = PrivateChat(user1_id=user_id_1, user2_id=user_id_2)
            self._session.add(chat)
            await self._session.commit()
            await self._session.refresh(chat)
            return chat
        except Exception as e:
            self._logger.error(
                f"Error at creating private chat {{user_a: {user_a}, user_b: {user_b}}}: {e}")
            raise DatabaseError(
                f"Error at creating private chat {{user_a: {user_a}, user_b: {user_b}}}: {e}") from e


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

    async def update_last_event(self, chat_id: int, last_message: str):
        try:
            private_chat_request = select(PrivateChat).where(
                PrivateChat.id_ == chat_id
            )
            result = await self._session.execute(private_chat_request)
            private_chat = result.scalar_one_or_none()
            private_chat.last_event_at = func.now()
            private_chat.last_message = last_message
            await self._session.commit()
            await self._session.refresh(private_chat)
        except Exception as e:
            raise DatabaseError() from e




