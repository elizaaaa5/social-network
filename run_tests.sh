#!/bin/bash

# Выход немедленно, если команда завершается с ненулевым статусом.
set -e

# Создание виртуального окружения и установка зависимостей
echo "Setting up virtual environment and installing dependencies..."
python3.12 -m venv venv
source venv/bin/activate
# Устанавливаем зависимости для обоих сервисов
pip3 install -r user-service/requirements.txt
pip3 install -r post-service/requirements.txt

# Запуск тестов user-service (не требуют Cassandra)
echo "Running user-service tests..."
pytest user-service

# --- Cassandra Setup ---
# Уникальное имя контейнера, чтобы избежать конфликтов
CONTAINER_NAME="test-cassandra-$(date +%s)"
echo "Starting Cassandra container ($CONTAINER_NAME)..."
# Запускаем Cassandra в фоновом режиме, используя стандартные креды
docker run -d --name $CONTAINER_NAME -p 9042:9042 -e CASSANDRA_USER=cassandra -e CASSANDRA_PASSWORD=cassandra cassandra:latest >&1

# Функция для остановки и удаления контейнера Cassandra
cleanup_cassandra() {
  echo "Stopping and removing Cassandra container ($CONTAINER_NAME)..."
  # Игнорируем ошибки, если контейнер уже остановлен/удален
  docker stop $CONTAINER_NAME >/dev/null 2>&1 || true
  docker rm $CONTAINER_NAME >/dev/null 2>&1 || true
  echo "Cassandra container cleanup finished."
}

trap cleanup_cassandra EXIT

echo "Waiting 10 seconds for Cassandra to initialize..."
sleep 30

# --- Post-Service Tests ---
# Установка переменных окружения для подключения тестов к Cassandra
export CASSANDRA_HOSTS="127.0.0.1"            # Подключаемся к localhost, т.к. порт проброшен
export CASSANDRA_KEYSPACE="post_service_test" # Используем отдельный keyspace для тестов
export CASSANDRA_USER="cassandra"             # Используем креды, заданные при старте контейнера
export CASSANDRA_PASSWORD="cassandra"

# Запуск тестов post-service
echo "Running post-service tests..."
pytest post-service

echo "All tests finished successfully."
# 'trap cleanup_cassandra EXIT' будет вызван автоматически здесь для очистки
