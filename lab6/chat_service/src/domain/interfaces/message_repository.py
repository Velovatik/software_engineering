from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.message import Message

class MessageRepository(ABC):
    @abstractmethod
    async def create(self, message: Message) -> Message:
        pass

    @abstractmethod
    async def get_by_id(self, message_id: str) -> Optional[Message]:
        pass

    @abstractmethod
    async def get_chat_messages(self, user1_id: int, user2_id: int) -> List[Message]:
        pass

    @abstractmethod
    async def get_user_messages(self, user_id: int) -> List[Message]:
        pass

    @abstractmethod
    async def update(self, message: Message) -> Optional[Message]:
        pass

    @abstractmethod
    async def delete(self, message_id: str) -> bool:
        pass 