from fastapi import APIRouter, Depends, Form, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, Post
from app.schemas import PostSchema, PostCreate
from app.utils import get_current_user, verify_post_owner, create_notification

router = APIRouter(tags=["Offers"])

@router.put("/{id}", response_model=PostSchema, status_code=status.HTTP_200_OK, name="Редактировать пост")
async def edit_post(id: int, payload: PostCreate = Form(...), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).filter(Post.id == id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")

    verify_post_owner(post, current_user)

    post.title = payload.title
    post.need = payload.need
    post.offer = payload.offer

    await db.commit()
    await db.refresh(post)

    # Отправляем уведомление автору на почту
    await create_notification(current_user.id, "Пост отредактирован", f"Ваш пост «{post.title}» был обновлён и отправлен на повторную модерацию.", db)

    return PostSchema.model_validate(post)