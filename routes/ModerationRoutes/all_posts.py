from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database import get_db
from app.models import Post
from app.utils import get_current_superuser

router = APIRouter(tags=["Moderation"])

@router.get("/pending", status_code=status.HTTP_200_OK, summary="Получить все посты на модерации")
async def get_pending_posts(db: AsyncSession = Depends(get_db), superuser=Depends(get_current_superuser)):
    result = await db.execute(select(Post).where(Post.status == "pending"))
    posts = result.scalars().all()
    return posts