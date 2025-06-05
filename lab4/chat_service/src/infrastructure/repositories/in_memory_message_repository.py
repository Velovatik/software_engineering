from typing import List, Dict
from ...domain.interfaces.message_repository import MessageRepository
from ...domain.entities.message import Message

class InMemoryMessageRepository(MessageRepository):
    def __init__(self):
        self.messages: List[Message] = []

    def save_message(self, message: Message) -> Message:
        self.messages.append(message)
        return message

    def get_user_messages(self, username: str) -> List[Message]:
        return [
            msg for msg in self.messages 
            if msg.sender == username or msg.receiver == username
        ] 