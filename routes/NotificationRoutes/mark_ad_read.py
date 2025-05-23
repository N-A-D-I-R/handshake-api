from fastapi import APIRouter, Depends, HTTPException, status

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.database import get_db
from app.models import Notification, User
from app.utils import get_current_user

router = APIRouter(tags=["Notifications"])

@router.post("/{notification_id}/read", status_code=status.HTTP_200_OK, summary="Отметить уведомление как прочитанное")
async def mark_as_read(
    notification_id: int, 
    current_user: Optional[User] = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходимо авторизоваться")

    stmt = update(Notification).where(Notification.id == notification_id, Notification.user_id == current_user.id).values(is_read=True)

    await db.execute(stmt)
    await db.commit()
    
    return {"message": "Уведомление отмечено как прочитанное"}