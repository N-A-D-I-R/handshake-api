import string
import random
import logging

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, Security, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from passlib.hash import bcrypt

from typing import Annotated, Optional

from .models import User, Post
from .auth import get_jwt_data, is_token_blacklisted
from .database import get_db

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)

# Обязательная проверка авторизации пользователя
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    jwt_token = credentials.credentials

    data = get_jwt_data(jwt_token, "access")
    user_id = data.get("id")

    if not user_id:
        logger.warning("JWT не содержит ID пользователя")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        logger.warning(f"Пользователь ID {user_id} не найден")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")

    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Пользователь не подтвердил почту")

    if await is_token_blacklisted(jwt_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен недействителен")

    return user

# Необязательная проверка авторизации пользователя
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if credentials is None:
        return None

    token = credentials.credentials
    try:
        data = get_jwt_data(token, "access")
        user_id = data.get("id")
        if not user_id:
            return None

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user or not user.is_verified:
            return None

        if await is_token_blacklisted(token):
            return None

        return user
    except Exception:
        return None

# Хеширование пароля перед сохранением в БД
def hash_password(password: str) -> str:
    return bcrypt.hash(password)

# Проверка введённого пароля против хешированного
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)

# Проверка владельца поста
def verify_post_owner(post: Post, user: User):
    if post.user_id != user.id:
        logger.warning("У пользователя нет прав на редактирование этого поста")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав на редактирование этого поста")
    
# Функция для генерации 6-значного кода
def generate_auth_key() -> str:
    return ''.join(random.choices(string.digits, k=6))

# Создание уведомления
async def create_notification(user_id: int, title: str, message: str, db: AsyncSession):
    from app.models import Notification
    notification = Notification(user_id=user_id, title=title, message=message)
    db.add(notification)
    await db.commit()