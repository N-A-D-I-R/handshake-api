from fastapi import HTTPException, APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Post
from app.schemas import PostSchema

router = APIRouter(tags=["Offers"])

@router.get("/pending/{id}", response_model=PostSchema, status_code=status.HTTP_200_OK, name="Открыть пост на модерации")
async def get_post(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == id, Post.status == "pending"))
    post = result.scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")

    return PostSchema.model_validate(post, from_attributes=True)