from fastapi import HTTPException, APIRouter, Depends, status

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Post, User
from app.schemas import PostSchema
from app.dependencies import get_current_user

router = APIRouter(tags=["Moderation"])

@router.get("/posts/{post_id}", response_model=PostSchema, status_code=status.HTTP_200_OK, name="Открыть пост на модерации")
async def get_post(
    post_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user or not current_user.is_moderator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Страница не найдена")

    result = await db.execute(select(Post).where(Post.id == post_id, Post.status == "pending"))
    post = result.scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")

    return PostSchema.model_validate(post, from_attributes=True)