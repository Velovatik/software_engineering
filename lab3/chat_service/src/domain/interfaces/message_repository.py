from abc import ABC, abstractmethod
from typing import List
from ..entities.message import Message

class MessageRepository(ABC):
    @abstractmethod
    def save_message(self, message: Message) -> Message:
        pass

    @abstractmethod
    def get_user_messages(self, username: str) -> List[Message]:
        pass 