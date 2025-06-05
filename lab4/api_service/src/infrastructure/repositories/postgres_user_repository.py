from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.entities.user import User as UserEntity, UserInDB
from src.domain.interfaces.user_repository import UserRepository
from src.infrastructure.database.models import User as UserModel
import bcrypt

class PostgresUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_password_hash(self, password: str) -> str:
        # hash pass using bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return password_hash.decode('utf-8')

    def create(self, user: UserInDB) -> UserEntity:
        # Extract password from either hashed_password or password field
        password_to_hash = user.hashed_password if hasattr(user, 'hashed_password') and user.hashed_password else user.password if hasattr(user, 'password') and user.password else ""
        password_hash = self.get_password_hash(password_to_hash)
        
        db_user = UserModel(
            username=user.username,
            password_hash=password_hash,
            role=getattr(user, 'role', 'user')
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return UserEntity(
            id=db_user.id,
            username=db_user.username,
            email=getattr(user, 'email', None),
            full_name=getattr(user, 'full_name', None),
            disabled=getattr(user, 'disabled', False),
            role=db_user.role,
            password=""  # We don't return the password hash
        )

    def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return None
        return UserEntity(
            id=db_user.id,
            username=db_user.username,
            email=None,
            full_name=None,
            disabled=False,
            role=db_user.role,
            password=""  # We don't return the password hash
        )

    def get_by_username(self, username: str) -> Optional[UserInDB]:
        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if not db_user:
            return None
        return UserInDB(
            id=db_user.id,
            username=db_user.username,
            hashed_password=db_user.password_hash,
            email=None,
            full_name=None,
            disabled=False,
            role=db_user.role
        )

    def get_all(self) -> List[UserEntity]:
        db_users = self.db.query(UserModel).all()
        return [
            UserEntity(
                id=user.id,
                username=user.username,
                email=None,
                full_name=None,
                disabled=False,
                role=user.role,
                password=""
            )
            for user in db_users
        ]

    def update(self, user: UserEntity) -> Optional[UserEntity]:
        db_user = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if not db_user:
            return None
        
        db_user.username = user.username
        if user.password:
            password_hash = self.get_password_hash(user.password)
            db_user.password_hash = password_hash
        db_user.role = user.role
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return UserEntity(
            id=db_user.id,
            username=db_user.username,
            password="",
            role=db_user.role
        )

    def delete(self, user_id: int) -> bool:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return False
        self.db.delete(db_user)
        self.db.commit()
        return True

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def verify_password_by_username(self, username: str, password: str) -> bool:
        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if not db_user:
            return False
        return self.verify_password(password, db_user.password_hash) 