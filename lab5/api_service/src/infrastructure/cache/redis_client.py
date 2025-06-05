import json
from typing import Optional, Any
import aioredis
from datetime import datetime

# Redis клиент для кэширования
# TODO: вынести конфиг в енв файл
REDIS_URL = "redis://redis:6379"
CACHE_TTL = 3600  # 1 час - можно будет поменять

class RedisClient:
    _instance = None
    _redis = None

    @classmethod
    async def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
            # надо бы добавить ретраи при подключении
            cls._redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        return cls._instance

    async def get(self, key: str) -> Optional[Any]:
        """Получить данные из кэша"""
        try:
            data = await self._redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Ошибка при чтении из кэша: {e}")  # заменить на нормальный логгер
        return None

    async def set(self, key: str, value: Any, ttl: int = CACHE_TTL) -> bool:
        """Записать данные в кэш"""
        try:
            # преобразуем datetime в строку для json
            if isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(v, datetime):
                        value[k] = v.isoformat()
            
            await self._redis.set(key, json.dumps(value), ex=ttl)
            return True
        except Exception as e:
            print(f"Не удалось записать в кэш: {e}")  # потом прикрутить нормальный логгер
            return False

    async def delete(self, key: str) -> bool:
        """Удалить данные из кэша"""
        try:
            await self._redis.delete(key)
            return True
        except Exception as e:
            print(f"Не удалось удалить из кэша: {e}")  # TODO: add proper logging
            return False

    async def clear_all(self) -> bool:
        """Очистить весь кэш (нужно для тестов)"""
        try:
            await self._redis.flushall()
            return True
        except Exception as e:
            print(f"Failed to clear cache: {e}")  # mixed lang comments - like a real person :)
            return False 