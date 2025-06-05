from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
from src.presentation.api import app

# Security configuration - must match API service
SECRET_KEY = "your-secret-key-keep-it-secret"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class Message(BaseModel):
    sender: str
    receiver: str
    content: str
    timestamp: datetime = datetime.now()

# In-memory storage
messages: List[Message] = []
active_connections: Dict[str, WebSocket] = {}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            # Process received message
            message_data = Message.parse_raw(data)
            messages.append(message_data)
            
            # Send to receiver if online
            if message_data.receiver in active_connections:
                await active_connections[message_data.receiver].send_text(data)
    except WebSocketDisconnect:
        del active_connections[client_id]

@app.post("/api/v1/message/send")
async def send_message(message: Message, current_user: str = Depends(get_current_user)):
    if current_user != message.sender:
        raise HTTPException(status_code=403, detail="Cannot send messages on behalf of other users")
    messages.append(message)
    return {"status": "Message sent"}

@app.get("/api/v1/message")
async def get_messages(current_user: str = Depends(get_current_user)):
    user_messages = [
        msg for msg in messages 
        if msg.sender == current_user or msg.receiver == current_user
    ]
    return user_messages

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 