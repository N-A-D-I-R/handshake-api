from fastapi import FastAPI
from routes.AuthRoutes import router as auth_router
from routes.PostsRoutes import router as post_router

import logging
import asyncio

from datetime import datetime

from sqlalchemy import delete

from .models import RefreshToken
from .database import get_db

from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Функция lifespan, которая выполняет код при запуске и завершении приложения"""

    logger.info("Инициализируем базу данных...")
    await init_db()
    logger.info("✅ База данных инициализирована")

    # Фоновая задача по удалению старых токенов
    async def cleanup():
        while True:
            async for db in get_db():
                await db.execute(delete(RefreshToken).where(RefreshToken.expires_at < datetime.utcnow()))
                await db.commit()
            await asyncio.sleep(3600)  # повтор через час

    # Запуск фонов задачи
    cleanup_task = asyncio.create_task(cleanup())

    # Даём FastAPI запуститься
    yield

    # Завершение работы приложения
    logger.info("🛑 Завершение работы приложения...")
    cleanup_task.cancel()  # Останавливаем фоновую задачу при завершении
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass  # Игнорируем ошибку отмены задачи

app = FastAPI(title="Handshake", description="...", openapi_prefix="/v1", lifespan=lifespan)

# Подключение роутеров
app.include_router(auth_router)
app.include_router(post_router)