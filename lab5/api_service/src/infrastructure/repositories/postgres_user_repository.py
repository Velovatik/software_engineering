from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.interfaces.user_repository import UserRepository
from src.domain.entities.user import User as UserEntity, UserInDB
from src.infrastructure.database.models import User as UserModel
from src.infrastructure.cache.redis_client import RedisClient
import bcrypt

class PostgresUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db
        # кэш инициализируется лениво при первом использовании
        self._cache = None

    async def _get_cache(self) -> RedisClient:
        """Ленивая инициализация кэша"""
        if not self._cache:
            self._cache = await RedisClient.get_instance()
        return self._cache

    def _user_to_dict(self, user: UserModel) -> dict:
        """Хелпер для сериализации юзера"""
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            # не сохраняем пароль в кэше ващет
        }

    def get_password_hash(self, password: str) -> str:
        """Hash a password using bcrypt"""
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
            password=""
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

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    # Additional methods for extended functionality
    async def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        # сначала смотрим в кэш
        cache = await self._get_cache()
        cached_user = await cache.get(f"user:{user_id}")
        
        if cached_user:
            # нашли в кэше - збс
            return UserEntity(
                id=cached_user["id"],
                username=cached_user["username"],
                password="",
                role=cached_user["role"]
            )

        # не нашли - лезем в базу
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return None

        # нашли - кэшируем и возвращаем
        await cache.set(f"user:{user_id}", self._user_to_dict(db_user))
        return UserEntity(
            id=db_user.id,
            username=db_user.username,
            password="",
            role=db_user.role
        )

    async def get_all(self) -> List[UserEntity]:
        # проверяем кэш для списка всех юзеров
        cache = await self._get_cache()
        cached_users = await cache.get("all_users")
        
        if cached_users:
            return [
                UserEntity(
                    id=user["id"],
                    username=user["username"],
                    password="",
                    role=user["role"]
                )
                for user in cached_users
            ]

        # не нашли - достаем из базы
        db_users = self.db.query(UserModel).all()
        users_data = [self._user_to_dict(user) for user in db_users]
        
        # кэшируем результат
        await cache.set("all_users", users_data)
        
        return [
            UserEntity(
                id=user.id,
                username=user.username,
                password="",
                role=user.role
            )
            for user in db_users
        ]

    async def update(self, user: UserEntity) -> Optional[UserEntity]:
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

        # инвалидируем все связанные ключи в кэше
        cache = await self._get_cache()
        await cache.delete(f"user:{user.id}")
        await cache.delete(f"user:name:{user.username}")
        await cache.delete("all_users")
        
        # обновляем кэш
        await cache.set(f"user:{db_user.id}", self._user_to_dict(db_user))
        await cache.set(f"user:name:{db_user.username}", self._user_to_dict(db_user))
        
        return UserEntity(
            id=db_user.id,
            username=db_user.username,
            password="",
            role=db_user.role
        )

    async def delete(self, user_id: int) -> bool:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return False

        # сначала удаляем из кэша
        cache = await self._get_cache()
        await cache.delete(f"user:{user_id}")
        await cache.delete(f"user:name:{db_user.username}")
        await cache.delete("all_users")

        # потом из базы
        self.db.delete(db_user)
        self.db.commit()
        return True

    # Legacy method for compatibility
    async def verify_password_by_username(self, username: str, password: str) -> bool:
        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if not db_user:
            return False
        return self.verify_password(password, db_user.password_hash) 