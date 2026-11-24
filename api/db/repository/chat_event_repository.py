import logging

from bson import ObjectId
from pymongo import DESCENDING
from pymongo.asynchronous.database import AsyncDatabase

from db.exceptions import DatabaseError


class ChatEventRepository:
    """События чата (сообщения, звонки, ...) в коллекции chat_events. Документы хранятся плоскими:
    {_id, chat_id, sender_id, created_at, event_type, ...поля конкретного типа}"""

    def __init__(self, db: AsyncDatabase):
        self._collection = db.chat_events
        self._logger = logging.getLogger("messenger.db")

    async def create(self, document: dict) -> dict:
        self._logger.info(f"Chat event create request {{chat_id: {document.get('chat_id')}, event_type: {document.get('event_type')}}}")
        try:
            # insert_one сам дописывает _id в document
            await self._collection.insert_one(document)
            return document
        except Exception as e:
            self._logger.error(f"Error at creating chat event {{chat_id: {document.get('chat_id')}}}: {e}")
            raise DatabaseError(f"Error at creating chat event {{chat_id: {document.get('chat_id')}}}") from e

    async def mark_projected(self, event_id: ObjectId):
        """Превью в Postgres обновлено — снимаем отметку outbox."""
        await self._collection.update_one({"_id": event_id}, {"$unset": {"outbox": ""}})

    async def find_pending(self, older_than, limit: int = 100) -> list[dict]:
        """События, превью которых ещё не применено к Postgres (сбой между записью в две базы)."""
        cursor = self._collection.find(
            {"outbox": {"$exists": True}, "created_at": {"$lt": older_than}}
        ).sort("created_at", 1).limit(limit)
        return await cursor.to_list()

    async def get_history(self, chat_id: int, limit: int = 50, before: ObjectId | None = None,
                          event_type: str | None = None) -> list[dict]:
        """Последние limit событий чата, новые первыми. before — _id самого старого уже загруженного события."""
        self._logger.info(f"Chat history request {{chat_id: {chat_id}, before: {before}, event_type: {event_type}}}")
        query = {"chat_id": chat_id}
        if before is not None:
            query["_id"] = {"$lt": before}
        if event_type is not None:
            query["event_type"] = event_type
        try:
            cursor = self._collection.find(query).sort("_id", DESCENDING).limit(limit)
            return await cursor.to_list()
        except Exception as e:
            self._logger.error(f"Error at requesting chat history {{chat_id: {chat_id}}}: {e}")
            raise DatabaseError(f"Error at requesting chat history {{chat_id: {chat_id}}}") from e
