from abc import ABC, abstractmethod
from typing import List
from ..entities.message import Message

class MessageRepository(ABC):
    @abstractmethod
    async def save_message(self, message: Message) -> Message:
        pass

    @abstractmethod
    async def get_user_messages(self, username: str) -> List[Message]:
        pass 