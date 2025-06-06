from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from app.database import get_db
from app.models import User
from app.schemas import FullUserProfile

router = APIRouter()

@router.get("/{id}", response_model=FullUserProfile, status_code=status.HTTP_200_OK, name="Профиль пользователя")
async def get_user(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).options(selectinload(User.posts)).where(User.id == id, User.is_verified == True))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    
    return user