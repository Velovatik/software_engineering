from typing import Optional
from ...domain.entities.user import User, UserInDB
from ...domain.interfaces.user_repository import UserRepository

class UserUseCases:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, user: User, password: str) -> User:
        hashed_password = self.user_repository.get_password_hash(password)
        user_in_db = UserInDB(**user.dict(), hashed_password=hashed_password)
        return self.user_repository.create(user_in_db)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.user_repository.get_by_username(username)
        if not user:
            return None
        if not self.user_repository.verify_password(password, user.hashed_password):
            return None
        return User(**user.dict())

    def get_user_by_username(self, username: str) -> Optional[User]:
        user = self.user_repository.get_by_username(username)
        if not user:
            return None
        return User(**user.dict()) 