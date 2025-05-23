from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.database import get_db
from app.models import Notification
from app.utils import get_current_user

router = APIRouter(tags=["Notifications"])

@router.delete("/{notification_id}", status_code=status.HTTP_200_OK, summary="Удалить уведомление")
async def delete_notification(notification_id: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = delete(Notification).where(Notification.id == notification_id, Notification.user_id == current_user.id)
    await db.execute(stmt)
    await db.commit()
    return {"message": "Уведомление удалено"}