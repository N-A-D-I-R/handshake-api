from fastapi import APIRouter, Depends, Form, HTTPException, status

from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import ProfileChangeRequest, User
from app.schemas import ProfileChangeCreate, MessageResponse
from app.dependencies import get_current_user

router = APIRouter()

@router.patch("/profile/edit", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, name="Изменение профиля")
async def profile_change(
    data: ProfileChangeCreate = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходимо авторизоваться")

    last_request = await db.execute(
        select(ProfileChangeRequest)
        .where(ProfileChangeRequest.user_id == current_user.id)
        .order_by(ProfileChangeRequest.created_at.desc())
        .limit(1)
    )
    last = last_request.scalar_one_or_none()
    if last and (datetime.now(timezone.utc) - last.created_at).days < 30:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Изменения доступны раз в 30 дней.")

    if data.new_username:
        username_check = await db.execute(
            select(User).where(User.username == data.new_username)
        )
        if username_check.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Имя пользователя уже занято.")

    change = ProfileChangeRequest(
        user_id=current_user.id,
        new_username=data.new_username,
        new_first_name=data.new_first_name,
        new_last_name=data.new_last_name,
        new_avatar_url=data.new_avatar_url
    )
    db.add(change)
    await db.commit()
    await db.refresh(change)

    return {"message": "Запрос на изменение профиля успешно создан"}