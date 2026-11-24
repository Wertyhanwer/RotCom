from pymongo import AsyncMongoClient, ASCENDING, DESCENDING
from pymongo.asynchronous.database import AsyncDatabase
import logging

from .configs.mongo_config import mongo_url, mongo_dbname
from db.exceptions import DatabaseError


class MongoEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self._logger = logging.getLogger("messenger.db")
        self._logger.info("Starting MongoEngine...")
        try:
            # tz_aware — чтобы даты возвращались с таймзоной (UTC), а не "голыми"
            self._client = AsyncMongoClient(mongo_url, tz_aware=True)
            self._db = self._client[mongo_dbname]
        except Exception as e:
            self._logger.critical(f"Critical error at creating Mongo client: {e}")
            raise DatabaseError("Critical error at creating Mongo client") from e

        self._initialized = True
        self._logger.info("MongoEngine successfully initialized")

    def get_db(self) -> AsyncDatabase:
        return self._db

    async def create_indexes(self):
        # история чата всегда читается по chat_id с сортировкой по _id (курсорная пагинация)
        await self._db.chat_events.create_index([("chat_id", ASCENDING), ("_id", DESCENDING)])
        # частичный индекс только по недоприменённым событиям — для досинхронизации превью
        await self._db.chat_events.create_index(
            [("created_at", ASCENDING)], name="pending_outbox",
            partialFilterExpression={"outbox": {"$exists": True}})

    async def close(self):
        await self._client.close()
