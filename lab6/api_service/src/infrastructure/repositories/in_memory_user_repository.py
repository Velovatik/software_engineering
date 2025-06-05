from typing import Optional, Dict
from passlib.context import CryptContext
from ...domain.interfaces.user_repository import UserRepository
from ...domain.entities.user import User, UserInDB

class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.users_db: Dict[str, dict] = {
            "admin": {
                "username": "admin",
                "full_name": "Administrator",
                "email": "admin@example.com",
                "hashed_password": self.get_password_hash("secret"),
                "disabled": False
            }
        }

    def create(self, user: UserInDB) -> User:
        if user.username in self.users_db:
            raise ValueError("Username already exists")
        user_dict = user.dict()
        self.users_db[user.username] = user_dict
        return User(**user_dict)

    def get_by_username(self, username: str) -> Optional[UserInDB]:
        if username not in self.users_db:
            return None
        return UserInDB(**self.users_db[username])

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password) 