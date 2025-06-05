from abc import ABC, abstractmethod
from typing import Optional
from ..entities.user import User, UserInDB

class UserRepository(ABC):
    @abstractmethod
    def create(self, user: UserInDB) -> User:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[UserInDB]:
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass

    @abstractmethod
    def get_password_hash(self, password: str) -> str:
        pass 