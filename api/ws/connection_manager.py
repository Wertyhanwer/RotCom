from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self._connections = dict()

    async def connect(self, user_id: int, websocket: WebSocket):
        self._connections[user_id] = websocket

    def disconnect(self, user_id: int):
        self._connections.pop(user_id, None)

    async def send_to(self, user_id: int, message: str):
        websocket = self._connections.get(user_id)
        if websocket:
            await websocket.send_text(message)




connection_manager = ConnectionManager()