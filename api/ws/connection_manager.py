import logging
from collections import defaultdict

from fastapi import WebSocket

logger = logging.getLogger("messenger.ws")


class ConnectionManager:
    """Активные WS-соединения в памяти процесса: user_id -> множество сокетов.

    У одного пользователя может быть несколько соединений (вкладки, устройства). Раньше
    хранился один сокет на user_id: новая вкладка вытесняла старую, а закрытие старой
    удаляло запись целиком, и новая вкладка переставала получать события.
    """

    def __init__(self):
        self._connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: int, websocket: WebSocket):
        self._connections[user_id].add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        sockets = self._connections.get(user_id)
        if sockets is None:
            return
        sockets.discard(websocket)
        if not sockets:
            del self._connections[user_id]

    async def send_to(self, user_id: int, message: str):
        # копия множества: disconnect() может изменить его во время await
        for websocket in list(self._connections.get(user_id, ())):
            try:
                await websocket.send_text(message)
            except Exception:
                logger.warning(f"Ws delivery failed, dropping socket: user_id={user_id}")
                self.disconnect(user_id, websocket)


connection_manager = ConnectionManager()
