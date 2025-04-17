#!/bin/bash

# Загрузим переменные из .env файла
export $(grep -v '^#' .env | xargs)

# Проверка наличия необходимых переменных окружения
if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
  echo "Ошибка: Необходимо задать переменные окружения DB_NAME, DB_USER и DB_PASSWORD."
  exit 1
fi

# Обновим список пакетов
echo "Обновляем список пакетов..."
apt update || { echo "Ошибка: Не удалось обновить список пакетов."; exit 1; }

# Установим PostgreSQL и Redis
echo "Устанавливаем PostgreSQL и Redis..."
if ! apt install -y postgresql postgresql-contrib redis-server; then
    echo "Ошибка: Не удалось установить PostgreSQL и/или Redis."
    exit 1
fi

# Проверка установки Redis
if ! command -v redis-server &> /dev/null; then
    echo "Ошибка: Redis не установлен."
    exit 1
fi

# Запускаем PostgreSQL
echo "Запускаем PostgreSQL..."
if ! service postgresql start; then
    echo "Ошибка: Не удалось запустить PostgreSQL."
    exit 1
fi

# Запускаем Redis
echo "Запускаем Redis..."
if ! service redis start; then
    echo "Ошибка: Не удалось запустить Redis."
    exit 1
fi

# Настроим PostgreSQL
echo "Настраиваем PostgreSQL..."
if ! sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"; then
    echo "Ошибка: Не удалось создать базу данных $DB_NAME."
    exit 1
fi

if ! sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"; then
    echo "Ошибка: Не удалось создать пользователя $DB_USER."
    exit 1
fi

if ! sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"; then
    echo "Ошибка: Не удалось предоставить привилегии пользователю $DB_USER."
    exit 1