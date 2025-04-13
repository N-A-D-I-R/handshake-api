from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, Post
from app.schemas import PostSchema, PostCreate
from app.utils import get_current_user

router = APIRouter(tags=["Posts"])

@router.post("/create", response_model=PostSchema, status_code=status.HTTP_201_CREATED, name="Создание поста")
async def create_post(
    payload: PostCreate = Query(...), 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    post = Post(**payload.model_dump(), user_id=current_user.id)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return PostSchema.model_validate(post)