from aiokafka import AIOKafkaProducer
import json
from typing import Any
import asyncio

# TODO: вынести в конфиг
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
USER_TOPIC = "user_events"  # топик для событий пользователей

class KafkaProducer:
    _instance = None
    _producer = None

    @classmethod
    async def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
            # создаем продюсера для кафки
            cls._producer = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            # надо бы добавить ретраи при подключении
            await cls._producer.start()
        return cls._instance

    async def send_message(self, value: Any) -> None:
        """Отправить сообщение в кафку"""
        try:
            await self._producer.send_and_wait(
                topic=USER_TOPIC,
                value=value
            )
        except Exception as e:
            print(f"Ошибка отправки в кафку: {e}")  # потом прикрутить нормальный логгер
            raise

    async def close(self) -> None:
        """Закрыть соединение с кафкой"""
        if self._producer:
            await self._producer.stop()
            self._producer = None 