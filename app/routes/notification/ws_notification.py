from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.notification_manager import notification_manager

router = APIRouter()

@router.websocket("/ws/notifications/{etablissement_id}")
async def websocket_notifications(websocket: WebSocket, etablissement_id: int):
    await notification_manager.connect(websocket, etablissement_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        notification_manager.disconnect(websocket)
