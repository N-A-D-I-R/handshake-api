import string
import random
import logging
import redis.asyncio as redis

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from typing import Annotated

from .models import User, Post
from .auth import get_jwt_data
from .database import get_db

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer()

# Проверка авторизации
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    jwt_token = credentials.credentials

    data = get_jwt_data(jwt_token, "refresh")

    user_id = data.get("id")
    if not user_id:
        logger.warning("Токен не содержит ID пользователя")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if await is_token_blacklisted(jwt_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен недействителен")

    if user is None:
        logger.warning(f"Пользователь с ID {user_id} не найден")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не авторизован"
        )

    return user

# Проверка владельца поста
def verify_post_owner(post: Post, user: User):
    if post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав на редактирование этого поста")
    
# Функция для генерации 6-значного кода
def generate_auth_key() -> str:
    return ''.join(random.choices(string.digits, k=6))
    
# Настройка подключения к Redis
async def get_redis_connection():
    return await redis.from_url("redis://localhost")

# Добавление токена в черный список
async def invalidate_access_token(jwt_token: str, ttl: int = 1):
    redis = await get_redis_connection()
    await redis.set(jwt_token, "blacklisted", ex=ttl)
    await redis.close()

# Проверка токена на действительность
async def is_token_blacklisted(jwt_token: str) -> bool:
    redis = await get_redis_connection()
    is_blacklisted = await redis.exists(jwt_token)
    await redis.close()
    return is_blacklisted