from typing import List, Dict
from fastapi import WebSocket
from ...domain.entities.message import Message
from ...domain.interfaces.message_repository import MessageRepository

class MessageUseCases:
    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository
        self.active_connections: Dict[str, WebSocket] = {}

    def save_message(self, message: Message) -> Message:
        return self.message_repository.save_message(message)

    def get_user_messages(self, username: str) -> List[Message]:
        return self.message_repository.get_user_messages(username)

    def add_websocket_connection(self, client_id: str, websocket: WebSocket):
        self.active_connections[client_id] = websocket

    def remove_websocket_connection(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def broadcast_message(self, message: Message):
        if message.receiver in self.active_connections:
            await self.active_connections[message.receiver].send_text(message.json()) 