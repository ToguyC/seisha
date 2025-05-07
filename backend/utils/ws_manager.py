import json
from typing import List

from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, event: str, data: dict = {}):
        for connection in self.active_connections:
            await connection.send_text(json.dumps({"event": event, "data": data}))

ws_instance = WebSocketManager()
