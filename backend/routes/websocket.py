from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..utils.ws_manager_insance import ws_instance

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_instance.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_instance.disconnect(websocket)
