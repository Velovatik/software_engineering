#!/bin/bash

# Скрипт для тестирования производительности с кэшем и без

# Сначала очищаем кэш Redis
echo "Очистка кэша Redis..."
redis-cli FLUSHALL

# Тестируем без кэша (первый запрос)
echo "Тест без кэша (1 поток):"
wrk -t1 -c1 -d30s http://localhost:8000/users/

echo "Тест без кэша (2 потока):"
wrk -t2 -c10 -d30s http://localhost:8000/users/

echo "Тест без кэша (4 потока):"
wrk -t4 -c50 -d30s http://localhost:8000/users/

# Делаем запрос для заполнения кэша
curl http://localhost:8000/users/ > /dev/null

# Тестируем с кэшем
echo "Тест с кэшем (1 поток):"
wrk -t1 -c1 -d30s http://localhost:8000/users/

echo "Тест с кэшем (2 потока):"
wrk -t2 -c10 -d30s http://localhost:8000/users/

echo "Тест с кэшем (4 потока):"
wrk -t4 -c50 -d30s http://localhost:8000/users/ 