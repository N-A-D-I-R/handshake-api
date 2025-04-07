from fastapi import FastAPI
from routes.AuthRoutes import router as auth_router
from routes.PostsRoutes import router as post_router

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager

from database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Функция lifespan, которая выполняет код при запуске и завершении приложения"""

    logger.info("Инициализируем базу данных...")

    await init_db()

    logger.info("✅ База данных инициализирована")
    
    yield  # Даем FastAPI запуститься

    logger.info("🛑 Завершение работы приложения...")
    # Здесь можно закрыть соединения, удалить временные файлы и т. д.

app = FastAPI(title="Handshake", description="...", openapi_prefix="/v1", lifespan=lifespan)
 
app.include_router(auth_router)
app.include_router(post_router)