from fastapi import APIRouter, Depends, HTTPException, status

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Notification, User
from app.schemas import NotificationSchema
from app.utils import get_current_user

router = APIRouter()

@router.get("/all", response_model=list[NotificationSchema], status_code=status.HTTP_200_OK, summary="Получить все уведомления")
async def get_notifications(
    current_user: Optional[User] = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходимо авторизоваться")

    result = await db.execute(select(Notification).where(Notification.user_id == current_user.id))
    return result.scalars().all()