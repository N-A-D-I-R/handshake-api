import jwt
import logging

import redis.asyncio as redis

from fastapi import HTTPException, Request, status
from datetime import datetime, timedelta, timezone

import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
REDIS_URL = os.getenv("REDIS_URL")

logger = logging.getLogger(__name__)

# Функции создания токенов
def create_token(user_id: int, token_type: str, lifetime: timedelta):
    payload = {
        "id": user_id,
        "type": token_type,
        "exp": datetime.now(timezone.utc) + lifetime
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_access_token(user_id: int):
    return create_token(user_id, token_type="access", lifetime=timedelta(minutes=15))


def create_refresh_token(user_id: int):
    return create_token(user_id, token_type="refresh", lifetime=timedelta(days=7))


def get_jwt_data(jwt_token: str, token_type: str):
    try:
        data = jwt.decode(jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        logger.warning("Токен истек")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия токена истек"
        )
    except jwt.DecodeError:
        logger.warning("Некорректный токен")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен"
        )

    if data.get("type") != token_type:
        logger.warning("Попытка использовать токен неверного типа")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный тип токена"
        )
    return data

# Настройка подключения к Redis
async def get_redis_connection():
    return await redis.from_url(REDIS_URL, decode_responses=True)

# Добавление токена в черный список
async def invalidate_access_token(jwt_token: str, ttl: int = 3600):
    redis = await get_redis_connection()
    await redis.set(jwt_token, "blacklisted", ex=ttl)
    await redis.close()

# Проверка токена на действительность
async def is_token_blacklisted(jwt_token: str) -> bool:
    redis = await get_redis_connection()
    is_blacklisted = await redis.exists(jwt_token)
    print(f"[Redis] Проверка токена {jwt_token} → {'в blacklist' if is_blacklisted else 'активен'}")
    await redis.close()
    return is_blacklisted

# Получение токена из заголовка запроса
def get_token_from_request(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ")[1]