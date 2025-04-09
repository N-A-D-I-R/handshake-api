# Используем официальный минимальный Python-образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем только файл зависимостей сначала
COPY requirements.txt .

# Устанавливаем нужные зависимости
RUN apt update && \
    apt install -y gcc libpq-dev libssl-dev build-essential && \
    pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копируем весь проект
COPY . .

# Открываем порт
EXPOSE 8000

# Устанавливаем переменные окружения для настройки среды
ENV ENVIRONMENT=development

# Запускаем FastAPI-приложение с учетом среды
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]