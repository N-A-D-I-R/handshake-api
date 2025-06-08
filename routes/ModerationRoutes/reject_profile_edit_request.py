from fastapi import APIRouter, Depends, HTTPException, status

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import ProfileChangeRequest, User
from app.schemas import MessageResponse
from app.dependencies import get_current_user
from app.utils import create_notification

router = APIRouter()

@router.post(
        "/users-profile-edit/{request_id}/reject", 
        response_model=MessageResponse,
        status_code=status.HTTP_200_OK, 
        name="Отклонить запрос на редактирование профиля"
)
async def reject_profile_change(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    if not current_user.is_moderator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Страница не найдена")

    result = await db.execute(select(ProfileChangeRequest).where(ProfileChangeRequest.id == request_id))
    change_request = result.scalar_one_or_none()

    if not change_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запрос не найден")

    await db.delete(change_request)
    await db.commit()

    user_result = await db.execute(select(User).where(User.id == change_request.user_id))
    user = user_result.scalar_one()

    # Отправляем уведомление автору на почту
    if user and user.email:
        from app.email import send_email, render_template
        html_body = render_template("profile_changes_rejected.html")
        await send_email(
            to=user.email,
            subject="Ваш запрос на изменение профиля отклонен",
            body=html_body,
            html=True
        )
    
    # Создаём уведомление
    await create_notification(user.id, "Смена данных профиля", "Ваша заявка на изменения профиля была отклонена", db)

    return {"message": "Изменения отклонены и удалены, пользователь уведомлен"}