#!/bin/bash

# Загрузим переменные из .env файла
export $(grep -v '^#' .env | xargs)

# Проверка наличия необходимых переменных окружения
if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
  echo "Ошибка: Необходимо задать переменные окружения DB_NAME, DB_USER и DB_PASSWORD."
  exit 1
fi

# Установим DEBIAN_FRONTEND для автоматического ответа на вопросы конфигурации
export DEBIAN_FRONTEND=noninteractive
export TERM=dumb

# Обновим список пакетов и установим PostgreSQL
apt update
apt install -y postgresql postgresql-contrib tzdata

# Настроим tzdata с помощью debconf
cat <<EOF | debconf-set-selections
tzdata tzdata/Areas select Etc
tzdata tzdata/Zones/Etc select UTC
EOF

# Настроим PostgreSQL
-u postgres psql -c "CREATE DATABASE $DB_NAME;"
-u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
-u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"


# Запустим PostgreSQL
systemctl start postgresql


echo "PostgreSQL установлен, настроен, таблица создана и база данных запущена."

pip3 install -r requirements.txt