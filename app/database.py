from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from .models import Base
from .settings import POSTGRESQL_DATABASE_URL, SQL_LOGGING

def str_to_bool(value: str) -> bool:
    return value.lower() in ("true", "1", "yes", "on")

switch_sql_logging = str_to_bool(SQL_LOGGING)

# Создание асинхронного движка PostgreSQL
engine = create_async_engine(
    POSTGRESQL_DATABASE_URL, 
    echo=switch_sql_logging,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
)

# Создание фабрики сессий
SessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession)

# Асинхронная зависимость для получения сессии БД
async def get_db():
    async with SessionLocal() as session:
        yield session