from sqlalchemy.ext.asyncio import AsyncSession
import logging
from sqlalchemy import select

from db.models.message import Message
from db.repository.private_chat_repository import PrivateChatRepository
from db.exceptions import DatabaseError

class MessageRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._logger = logging.getLogger("messenger.db")

    async def create(self, chat_id: int, from_user_id: int, content: str) -> Message:
        self._logger.info(f"Message create request {{chat_id: {chat_id}, from_user_id: {from_user_id}}}")
        try:
            message = Message(chat_id=chat_id, from_user_id=from_user_id, content=content)
            self._session.add(message)
            await self._session.commit()
            await self._session.refresh(message)
            await PrivateChatRepository(self._session).update_last_event(chat_id, content)
            return message
        except Exception as e:
            self._logger.error(f"Error at user creating message {{chat_id: {chat_id}, from_user_id: {from_user_id}}}: {e}")
            raise DatabaseError(f"Error at user creating message {{chat_id: {chat_id}, from_user_id: {from_user_id}}}") from e

    async def get_by_chat_id(self, chat_id: int, limit: int = 50, offset: int = 0) -> list[Message]:
        self._logger.info(f"Message get request {{chat_id: {chat_id}}}")
        try:
            messages_request = select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at).limit(limit).offset(offset)
            messages = await self._session.execute(messages_request)
            return messages.scalars().all()

        except Exception as e:
            self._logger.error(f"Error at user requesting messages {{chat_id: {chat_id}}}: {e}")
            raise DatabaseError(f"Error at user requesting messages {{chat_id: {chat_id}}}: {e}") from e