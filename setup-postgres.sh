#!/bin/bash

# Загрузим переменные из .env файла
export $(grep -v '^#' .env | xargs)

# Проверка наличия необходимых переменных окружения
if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
  echo "Ошибка: Необходимо задать переменные окружения DB_NAME, DB_USER и DB_PASSWORD."
  exit 1
fi

# Обновим список пакетов и установим PostgreSQL
apt update
apt install -y postgresql postgresql-contrib sudo redis-server

# Настроим PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo "PostgreSQL установлен, настроен, таблица создана и база данных запущена."