from fastapi import APIRouter, Depends, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, Post
from app.schemas import PostCreate
from app.utils import get_current_user, create_notification

router = APIRouter(tags=["Posts"])

@router.post("/create", status_code=status.HTTP_201_CREATED, name="Создание поста")
async def create_post(
    payload: PostCreate = Form(...), 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    post = Post(**payload.model_dump(), user_id=current_user.id)
    db.add(post)
    await db.commit()
    await db.refresh(post)

    # Отправляем уведомление автору на почту
    await create_notification(current_user.id, "Пост отправлен на модерацию", f"Ваш пост «{post.title}» ожидает одобрения.", db)

    return {"message": "Пост успешно создан и отправлен на модерацию"}