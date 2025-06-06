from fastapi import APIRouter, Depends, HTTPException, status

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import ProfileChangeRequest, User
from app.schemas import ProfileChangeOut
from app.utils import get_current_user

router = APIRouter()

@router.get(
    "/users-profile-edit/{request_id}",
    response_model=ProfileChangeOut,
    status_code=status.HTTP_200_OK,
    name="Детали запроса на изменение профиля"
)
async def get_profile_edit_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user or not current_user.is_moderator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Страница не найдена")

    result = await db.execute(
        select(ProfileChangeRequest).where(ProfileChangeRequest.id == request_id)
    )
    request = result.scalar_one_or_none()

    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запрос не найден")

    return request