from fastapi import APIRouter, Depends, HTTPException, status

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import ProfileChangeRequest, User
from app.schemas import MessageResponse
from app.utils import get_current_user, create_notification

router = APIRouter()

@router.post(
        "/users-profile-edit/{request_id}/approve", 
        response_model=MessageResponse,
        status_code=status.HTTP_200_OK, 
        name="Одобрение запроса на редактирование профиля"
)
async def approve_profile_change(
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
    
    user_result = await db.execute(select(User).where(User.id == change_request.user_id))
    user = user_result.scalar_one()

    if change_request.new_username:
        user.username = change_request.new_username
    if change_request.new_first_name:
        user.first_name = change_request.new_first_name
    if change_request.new_last_name:
        user.last_name = change_request.new_last_name
    if change_request.new_avatar_url:
        user.avatar_url = change_request.new_avatar_url

    await db.delete(change_request)
    await db.commit()

    # Отправляем уведомление автору на почту
    if user and user.email:
        from app.email import send_email, render_template
        html_body = render_template(
            "profile_changes_approved.html", 
            new_first_name=user.first_name, 
            new_last_name=user.last_name, 
            new_username=user.username
        )
        await send_email(
            to=user.email,
            subject="Ваш запрос на изменение профиля одобрен",
            body=html_body,
            html=True
        )
    
    # Создаём уведомление
    await create_notification(user.id, "Смена данных профиля","Ваша заявка на изменения профиля была одобрена", db)

    return {"message": "Изменения одобрены и применены, пользователь уведомлен"}
