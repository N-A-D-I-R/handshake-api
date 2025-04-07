from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from app.models import User, Post
from app.schemas import PostSchema, PostCreate
from app.utils import get_current_user, verify_post_owner

router = APIRouter(tags=["Posts"])

@router.put("/posts/{id}", response_model=PostSchema, status_code=status.HTTP_200_OK, name="Редактирование поста")
async def edit_post(id: int, payload: PostCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).filter(Post.id == id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")

    verify_post_owner(post, current_user)

    post.text = payload.text
    post.title = payload.title

    await db.commit()
    await db.refresh(post)

    return PostSchema.model_validate(post)