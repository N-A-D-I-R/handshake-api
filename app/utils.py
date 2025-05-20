import string
import random
import logging

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException, Request, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from passlib.hash import bcrypt

from typing import Annotated

from .models import User, Post
from .auth import get_jwt_data, is_token_blacklisted
from .database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer()

# Проверка авторизации пользователя
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    jwt_token = credentials.credentials

    data = get_jwt_data(jwt_token, "access")
    user_id = data.get("id")

    if not user_id:
        logger.info("JWT не содержит ID пользователя")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        logger.info(f"Пользователь ID {user_id} не найден")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")

    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Пользователь не подтвердил почту")

    if await is_token_blacklisted(jwt_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен недействителен")

    return user

# Контроллер для передачи запроса в параметры функции проверки пользователя
async def get_current_user_from_request(request: Request, db: AsyncSession) -> User:
    credentials = await bearer_scheme(request)
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Нет токена")
    return await get_current_user(credentials, db)

# Хеширование пароля перед сохранением в БД
def hash_password(password: str) -> str:
    return bcrypt.hash(password)

# Проверка введённого пароля против хешированного
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)

# Проверка владельца поста
def verify_post_owner(post: Post, user: User):
    if post.user_id != user.id:
        logger.info("У пользователя нет прав на редактирование этого поста")
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