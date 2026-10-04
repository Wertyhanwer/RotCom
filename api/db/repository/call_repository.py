from sqlalchemy.ext.asyncio import AsyncSession
import logging
from sqlalchemy import select

from db.models.call import Call, CallStatus
from db.exceptions import DatabaseError


class CallRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._logger = logging.getLogger("messenger.db")

    async def create(self, chat_id: int, caller_id: int, status: CallStatus, duration: int) -> Call:
        self._logger.info(f"Call create request {{chat_id: {chat_id}, caller_id: {caller_id}}}")
        try:
            call = Call(chat_id=chat_id, caller_id=caller_id, status=status, duration=duration)
            self._session.add(call)
            await self._session.commit()
            await self._session.refresh(call)
            return call
        except Exception as e:
            self._logger.error(f"Error at creating call {{chat_id: {chat_id}, caller_id: {caller_id}}}: {e}")
            raise DatabaseError(f"Error at creating call {{chat_id: {chat_id}, caller_id: {caller_id}}}") from e

    async def get_by_chat_id(self, chat_id: int, limit: int = 50, offset: int = 0) -> list[Call]:
        self._logger.info(f"Call get request {{chat_id: {chat_id}}}")
        try:
            calls_request = select(Call).where(Call.chat_id == chat_id).order_by(Call.created_at).limit(limit).offset(offset)
            calls = await self._session.execute(calls_request)
            return calls.scalars().all()
        except Exception as e:
            self._logger.error(f"Error at requesting calls {{chat_id: {chat_id}}}: {e}")
            raise DatabaseError(f"Error at requesting calls {{chat_id: {chat_id}}}: {e}") from e
