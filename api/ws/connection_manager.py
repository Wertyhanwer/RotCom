import asyncio
import json
import logging
import os
from collections import defaultdict

from fastapi import WebSocket
from redis.asyncio import Redis

logger = logging.getLogger("messenger.ws")

REDIS_URL = os.getenv("REDIS_URL", "")
CHANNEL = "rotcom:ws_events"


class ConnectionManager:
    """Доставка WS-событий пользователям.

    Сокеты живут в памяти конкретного процесса: user_id -> множество сокетов (вкладки, устройства).
    Если api запущен в нескольких процессах или репликах, получатель может быть подключён к
    другому процессу. Поэтому при заданном REDIS_URL событие публикуется в канал Redis Pub/Sub,
    каждый процесс подписан на этот канал и доставляет событие своим локальным сокетам.
    Без REDIS_URL (локальная разработка, один процесс) доставка идёт напрямую.
    """

    def __init__(self):
        self._connections: dict[int, set[WebSocket]] = defaultdict(set)
        self._redis: Redis | None = None
        self._listener: asyncio.Task | None = None
        self._subscribed = asyncio.Event()

    # ------------------------------------------------------------------ жизненный цикл

    async def start(self, redis_url: str = REDIS_URL):
        if not redis_url:
            logger.warning("REDIS_URL is not set: WS events are delivered only within this process")
            return
        self._redis = Redis.from_url(redis_url)
        self._listener = asyncio.create_task(self._listen())
        # ждём первую подписку, чтобы не потерять события сразу после старта
        try:
            await asyncio.wait_for(self._subscribed.wait(), timeout=10)
        except asyncio.TimeoutError:
            logger.error("Redis subscription is not ready, will keep retrying in background")

    async def stop(self):
        if self._listener is not None:
            self._listener.cancel()
            try:
                await self._listener
            except asyncio.CancelledError:
                pass
        if self._redis is not None:
            await self._redis.aclose()

    async def _listen(self):
        """Подписка на канал с переподключением: обрыв связи с Redis не должен убивать доставку навсегда."""
        while True:
            try:
                async with self._redis.pubsub() as pubsub:
                    await pubsub.subscribe(CHANNEL)
                    self._subscribed.set()
                    logger.info("Subscribed to Redis channel for WS events")
                    async for message in pubsub.listen():
                        if message["type"] != "message":
                            continue
                        data = json.loads(message["data"])
                        await self._deliver_local(data["user_id"], data["payload"])
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self._subscribed.clear()
                logger.error(f"Redis subscription failed, reconnecting: {e}")
                await asyncio.sleep(1)

    # ------------------------------------------------------------------ соединения

    async def connect(self, user_id: int, websocket: WebSocket):
        self._connections[user_id].add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        sockets = self._connections.get(user_id)
        if sockets is None:
            return
        sockets.discard(websocket)
        if not sockets:
            del self._connections[user_id]

    # ------------------------------------------------------------------ доставка

    async def send_to(self, user_id: int, message: str):
        if self._redis is None:
            await self._deliver_local(user_id, message)
            return
        try:
            await self._redis.publish(CHANNEL, json.dumps({"user_id": user_id, "payload": message}))
        except Exception as e:
            # Redis недоступен — доставим хотя бы тем, кто подключён к этому процессу
            logger.error(f"Redis publish failed, delivering locally only: {e}")
            await self._deliver_local(user_id, message)

    async def _deliver_local(self, user_id: int, message: str):
        # копия множества: disconnect() может изменить его во время await
        for websocket in list(self._connections.get(user_id, ())):
            try:
                await websocket.send_text(message)
            except Exception:
                logger.warning(f"Ws delivery failed, dropping socket: user_id={user_id}")
                self.disconnect(user_id, websocket)


connection_manager = ConnectionManager()
