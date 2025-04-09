# Используем официальный минимальный Python-образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем только файл зависимостей сначала
COPY requirements.txt .

# Обновляем apt и устанавливаем необходимые пакеты для сборки зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc libpq-dev libssl-dev build-essential && \
    # Устанавливаем Python-пакеты
    pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    # Очищаем кэш apt
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копируем весь проект в контейнер
COPY . .

# Открываем порт
EXPOSE 8000

# Устанавливаем переменные окружения для настройки среды
ENV ENVIRONMENT=development
ENV JWT_SECRET=${JWT_SECRET}
ENV JWT_ALGORITHM=${JWT_ALGORITHM}
ENV POSTGRESQL_DATABASE_URL=${POSTGRESQL_DATABASE_URL}
ENV DEBUG=${DEBUG}
ENV PORT=${PORT}

# Запускаем FastAPI-приложение с учетом среды
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]