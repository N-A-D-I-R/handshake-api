import logging
import asyncio

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware

from routes.AuthRoutes import router as auth_router
from routes.UsersRoutes import router as users_router
from routes.PostsRoutes import router as offers_router
from routes.SettingsRoutes import router as settings_router
from routes.ModerationRoutes import router as moderation_router
from routes.NotificationRoutes import router as notification_router

from sqlalchemy import delete

from datetime import datetime, timedelta, timezone

from app.models import User, Notification
from app.database import get_db, init_db

from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
                now = datetime.now(timezone.utc)
                month_ago = now - timedelta(days=30)

                # Удаляем неподтвержденных пользователей
                await db.execute(
                    delete(User).where(User.is_verified == False)
                )

                # Удаляем уведомления старше месяца
                await db.execute(
                    delete(Notification).where(Notification.created_at < month_ago)
                )

                await db.commit()
                logger.info("🧹 Очистка завершена")

            await asyncio.sleep(1800)

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

app = FastAPI(title="GoBarter", description=False, root_path="/api/v1", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["http://localhost:8080", "https://gobarter.ru", "https://гобартер.рф"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(offers_router)
app.include_router(notification_router)
app.include_router(settings_router)
app.include_router(moderation_router)

add_pagination(app)