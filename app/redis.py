import logging
import redis.asyncio as redis

from fastapi import HTTPException, status
from .settings import REDIS_URL, CODE_EXPIRATION

logger = logging.getLogger(__name__)

# Настройка подключения к Redis
async def get_redis_connection():
    return await redis.from_url(REDIS_URL, decode_responses=True)

# Добавление кода подтверждения
async def add_verification_code(email: str, code: str, ttl: int = CODE_EXPIRATION):
    redis = await get_redis_connection()
    await redis.set(email, code, ex=ttl)
    await redis.close()

# Сохранение нового email и кода подтверждения для смены почты
async def save_email_change(user_id: int, new_email: str, code: str, ttl: int = CODE_EXPIRATION):
    redis = await get_redis_connection()
    await redis.set(f"email_change:{user_id}", new_email, ex=ttl)
    await redis.set(f"email_code:{new_email}", code, ex=ttl)
    await redis.close()

# Проверка кода подтверждения
async def check_verification_code(email: str, code: str) -> bool:
    redis = await get_redis_connection()
    stored_code = await redis.get(email)

    if not stored_code:
        logger.warning("Код подтверждения не найден или просрочен")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Код подтверждения просрочен")

    if stored_code != code:
        logger.warning("Неверный код подтверждения")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный код подтверждения")

    await redis.delete(email)
    await redis.close()

# Добавление токенов в черный список
async def invalidate_access_token(jwt_token: str, ttl: int):
    redis = await get_redis_connection()
    await redis.set(jwt_token, "blacklisted", ex=ttl)
    await redis.close()

async def invalidate_refresh_token(jwt_token: str, ttl: int):
    redis = await get_redis_connection()
    await redis.set(jwt_token, "blacklisted", ex=ttl)
    await redis.close()

# Проверка токена на действительность
async def is_token_blacklisted(jwt_token: str) -> bool:
    redis = await get_redis_connection()
    is_blacklisted = await redis.exists(jwt_token)
    await redis.close()
    return is_blacklisted

# Генерация ключей
def create_redis_key(prefix: str, value: str) -> str:
    return f"{prefix}:{value}"