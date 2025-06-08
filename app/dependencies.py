import logging

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, Security, HTTPException, Request, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from typing import Optional

from .models import User, Post
from .token import get_jwt_data
from .redis import is_token_blacklisted
from .database import get_db

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)

# Проверка авторизации пользователя
async def get_current_user(
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

# Проверка владельца поста
def verify_post_owner(post: Post, user: User):
    if post.user_id != user.id:
        logger.warning("У пользователя нет прав на редактирование этого поста")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав на редактирование этого поста")
    
# Получение токена из заголовка запроса
def get_token_from_request(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ")[1]