from fastapi import APIRouter, Depends, HTTPException, status

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.database import get_db
from app.models import Notification, User
from app.schemas import MessageResponse
from app.utils import get_current_user

router = APIRouter()

@router.delete("/delete/{notification_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK, summary="Удалить уведомление")
async def delete_notification(
    notification_id: int, 
    current_user: Optional[User] = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходимо авторизоваться")

    stmt = delete(Notification).where(Notification.id == notification_id, Notification.user_id == current_user.id)

    await db.execute(stmt)
    await db.commit()
    
    return {"message": "Уведомление удалено"}