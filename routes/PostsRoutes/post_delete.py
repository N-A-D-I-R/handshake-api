from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, Post
from app.schemas import PostSchema
from app.utils import get_current_user, verify_post_owner, create_notification

router = APIRouter(tags=["Posts"])

@router.delete("/{id}", response_model=PostSchema, status_code=status.HTTP_200_OK, name="Удаление поста")
async def delete_post(id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).filter(Post.id == id))
    post = result.scalars().first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")

    verify_post_owner(post, current_user)

    await db.delete(post)
    await db.commit()

    # Отправляем уведомление автору на почту
    await create_notification(current_user.id, "Пост удален", f"Ваш пост «{post.title}» был удален.", db)

    return PostSchema.model_validate(post)