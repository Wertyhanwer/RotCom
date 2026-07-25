from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging

from db.exceptions import DatabaseError


class ChatHistoryRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._logger = logging.getLogger("messenger.db")

    async def get_history(self, chat_id: int, limit: int = 50, offset: int = 0) -> list:
        self._logger.info(f"Chat history request {{chat_id: {chat_id}}}")
        try:
            query = text("""
                SELECT id, chat_id, from_user_id, created_at, 'message' AS event_type,
                       content, NULL AS status, NULL AS duration, NULL AS caller_id
                FROM messages
                WHERE chat_id = :chat_id

                UNION ALL

                SELECT id, chat_id, NULL AS from_user_id, created_at, 'call' AS event_type,
                       NULL AS content, status::text AS status, duration, caller_id
                FROM calls
                WHERE chat_id = :chat_id

                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """)
            result = await self._session.execute(query, {"chat_id": chat_id, "limit": limit, "offset": offset})
            return result.mappings().all()
        except Exception as e:
            self._logger.error(f"Error at requesting chat history {{chat_id: {chat_id}}}: {e}")
            raise DatabaseError(f"Error at requesting chat history {{chat_id: {chat_id}}}") from e
