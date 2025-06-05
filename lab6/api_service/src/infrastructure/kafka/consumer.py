from aiokafka import AIOKafkaConsumer
import json
import asyncio
from typing import Callable, Any

# TODO: вынести в конфиг
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
USER_TOPIC = "user_events"

class KafkaConsumer:
    def __init__(self, message_handler: Callable[[dict], Any]):
        self.consumer = None
        self.message_handler = message_handler
        self._running = False

    async def start(self):
        """Запустить консьюмера"""
        if self._running:
            return

        self.consumer = AIOKafkaConsumer(
            USER_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id="user_events_group",  # группа для consumer'ов
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset="earliest"  # начинаем читать с начала если нет offset'а
        )
        
        await self.consumer.start()
        self._running = True
        
        try:
            async for msg in self.consumer:
                try:
                    await self.message_handler(msg.value)
                except Exception as e:
                    print(f"Ошибка обработки сообщения: {e}")  # потом прикрутить нормальный логгер
        finally:
            await self.stop()

    async def stop(self):
        """Остановить консьюмера"""
        if self.consumer:
            await self.consumer.stop()
            self._running = False 