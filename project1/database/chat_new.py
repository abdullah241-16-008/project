# ==================== CHAT WEBSOCKET SERVER ====================
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .message_service import save_message
from datetime import datetime

app = FastAPI()

# user_id -> websocket
active_users = {}

@app.websocket("/ws/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: int):
    await websocket.accept()
    active_users[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_json()

            sender_id    = int(data["sender_id"])
            receiver_id  = int(data["receiver_id"])
            message_text = data["message"].strip()

            # ignore empty messages
            if not message_text:
                continue

            await save_message(sender_id, receiver_id, message_text)

            msg = {
                "sender_id"  : sender_id,
                "receiver_id": receiver_id,
                "message"    : message_text,
                "timestamp"  : datetime.now().isoformat()
            }

            # send to receiver if online
            if receiver_id in active_users:
                await active_users[receiver_id].send_json(msg)

            # confirm to sender
            await websocket.send_json({"status": "ok"})

    except WebSocketDisconnect:
        del active_users[user_id]