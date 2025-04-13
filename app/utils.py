import string
import random
import logging
import redis.asyncio as redis

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from passlib.hash import bcrypt

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

    data = get_jwt_data(jwt_token, "access")
    user_id = data.get("id")

    if not user_id:
        logger.warning("JWT не содержит ID пользователя")
        raise HTTPException(status_code=401, detail="Недействительный токен")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        logger.warning(f"Пользователь ID {user_id} не найден")
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Пользователь не подтвердил почту")

    if await is_token_blacklisted(jwt_token):
        raise HTTPException(status_code=401, detail="Токен недействителен")

    return user

# Хеширование пароля перед сохранением в БД
def hash_password(password: str) -> str:
    return bcrypt.hash(password)

# Проверка введённого пароля против хешированного
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)

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