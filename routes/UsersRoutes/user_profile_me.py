from fastapi import APIRouter, Depends, HTTPException, status

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from app.database import get_db
from app.models import User
from app.schemas import UserMe
from app.utils import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserMe, status_code=status.HTTP_200_OK, name="Профиль пользователя")
async def get_user(
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходимо авторизоваться")

    result = await db.execute(
        select(User)
        .options(selectinload(User.posts))
        .where(User.id == current_user.id, User.is_verified == True)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    return UserMe(
        **user.__dict__,
        is_moderator=user.is_moderator,
        posts=user.posts
    )