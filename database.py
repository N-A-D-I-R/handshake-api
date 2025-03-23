from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import POSTGRESQL_DATABASE_URL

from app.models import Base

# Создание асинхронного движка PostgreSQL
engine = create_async_engine(POSTGRESQL_DATABASE_URL, echo=True)

# Создание фабрики сессий
SessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession)


# Функция инициализации базы данных
async def init_db():
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE EXTENSION IF NOT EXISTS pg_trgm;
        """))

        await conn.run_sync(Base.metadata.create_all)

# Асинхронная зависимость для получения сессии БД


async def get_db():
    async with SessionLocal() as session:
        yield session
