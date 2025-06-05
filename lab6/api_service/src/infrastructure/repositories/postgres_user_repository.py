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

    async def create(self, user: UserEntity) -> UserInDB:
        # хэшируем пароль как обычно
        password_hash = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        db_user = UserModel(
            username=user.username,
            password_hash=password_hash.decode('utf-8'),
            role=user.role
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        # инвалидируем кэш списка всех юзеров
        cache = await self._get_cache()
        await cache.delete("all_users")
        
        # кэшируем нового юзера
        await cache.set(f"user:{db_user.id}", self._user_to_dict(db_user))
        await cache.set(f"user:name:{db_user.username}", self._user_to_dict(db_user))

        return UserInDB(
            id=db_user.id,
            username=db_user.username,
            password=password_hash.decode('utf-8'),
            role=db_user.role
        )

    async def get_by_id(self, user_id: int) -> Optional[UserInDB]:
        # сначала смотрим в кэш
        cache = await self._get_cache()
        cached_user = await cache.get(f"user:{user_id}")
        
        if cached_user:
            # нашли в кэше - збс
            db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
            if db_user:
                return UserInDB(
                    id=cached_user["id"],
                    username=cached_user["username"],
                    password=db_user.password_hash,
                    role=cached_user["role"]
                )

        # не нашли - лезем в базу
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return None

        # нашли - кэшируем и возвращаем
        await cache.set(f"user:{user_id}", self._user_to_dict(db_user))
        return UserInDB(
            id=db_user.id,
            username=db_user.username,
            password=db_user.password_hash,
            role=db_user.role
        )

    async def get_by_username(self, username: str) -> Optional[UserInDB]:
        # то же самое для поиска по юзернейму
        cache = await self._get_cache()
        cached_user = await cache.get(f"user:name:{username}")
        
        if cached_user:
            db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
            if db_user:
                return UserInDB(
                    id=cached_user["id"],
                    username=cached_user["username"],
                    password=db_user.password_hash,
                    role=cached_user["role"]
                )

        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if not db_user:
            return None

        await cache.set(f"user:name:{username}", self._user_to_dict(db_user))
        return UserInDB(
            id=db_user.id,
            username=db_user.username,
            password=db_user.password_hash,
            role=db_user.role
        )

    async def get_all(self) -> List[UserInDB]:
        # проверяем кэш для списка всех юзеров
        cache = await self._get_cache()
        cached_users = await cache.get("all_users")
        
        if cached_users:
            # Для get_all нужно получить полные данные из базы
            db_users = self.db.query(UserModel).all()
            return [
                UserInDB(
                    id=user.id,
                    username=user.username,
                    password=user.password_hash,
                    role=user.role
                )
                for user in db_users
            ]

        # не нашли - достаем из базы
        db_users = self.db.query(UserModel).all()
        users_data = [self._user_to_dict(user) for user in db_users]
        
        # кэшируем результат
        await cache.set("all_users", users_data)
        
        return [
            UserInDB(
                id=user.id,
                username=user.username,
                password=user.password_hash,
                role=user.role
            )
            for user in db_users
        ]

    async def update(self, user: UserEntity) -> Optional[UserInDB]:
        db_user = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if not db_user:
            return None
        
        db_user.username = user.username
        if user.password:
            password_hash = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
            db_user.password_hash = password_hash.decode('utf-8')
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
        
        return UserInDB(
            id=db_user.id,
            username=db_user.username,
            password=db_user.password_hash,
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

    async def verify_password(self, username: str, password: str) -> bool:
        # для проверки пароля всегда идем в базу
        # не храним хэши в кэше из соображений безопасности
        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if not db_user:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), db_user.password_hash.encode('utf-8'))
    
    def get_password_hash(self, password: str) -> str:
        """Хэширует пароль"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')