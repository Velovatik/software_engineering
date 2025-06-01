from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List

from ..domain.entities.message import Message
from ..application.use_cases.message_use_cases import MessageUseCases
from ..application.auth.jwt_handler import JWTHandler
from ..infrastructure.repositories.in_memory_message_repository import InMemoryMessageRepository

# Configuration
SECRET_KEY = "your-secret-key-keep-it-secret"

# Setup
app = FastAPI(title="Chat Service")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependencies
message_repository = InMemoryMessageRepository()
message_use_cases = MessageUseCases(message_repository)
jwt_handler = JWTHandler(SECRET_KEY)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    username = jwt_handler.decode_token(token)
    if username is None:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    message_use_cases.add_websocket_connection(client_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = Message.parse_raw(data)
            message_use_cases.save_message(message)
            await message_use_cases.broadcast_message(message)
    except WebSocketDisconnect:
        message_use_cases.remove_websocket_connection(client_id)

@app.post("/api/v1/message/send")
async def send_message(message: Message, current_user: str = Depends(get_current_user)):
    if current_user != message.sender:
        raise HTTPException(status_code=403, detail="Cannot send messages on behalf of other users")
    saved_message = message_use_cases.save_message(message)
    await message_use_cases.broadcast_message(saved_message)
    return {"status": "Message sent"}

@app.get("/api/v1/message", response_model=List[Message])
async def get_messages(current_user: str = Depends(get_current_user)):
    return message_use_cases.get_user_messages(current_user) 