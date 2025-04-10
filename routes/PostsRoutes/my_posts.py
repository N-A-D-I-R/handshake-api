from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text

from app.database import get_db
from app.models import User, Post
from app.schemas import PostSchema
from app.utils import get_current_user

router = APIRouter(tags=["Posts"])

@router.get("/my", response_model=list[PostSchema], status_code=status.HTTP_200_OK, name="Поиск моих постов")
async def get_my_posts(title: str = None, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if title:
        result = await db.execute(text("""
            SELECT id, title, need, offer, user_id
            FROM posts
            WHERE user_id = :user_id AND (
                search_vector @@ plainto_tsquery('russian', :title)
                OR similarity(title, :title) > 0.2
            )
            ORDER BY ts_rank(search_vector, plainto_tsquery('russian', :title)) DESC,
                     similarity(title, :title) DESC
            LIMIT 10
        """).bindparams(user_id=current_user.id, title=title))
        
        rows = result.fetchall()
        posts = [Post(id=row[0], title=row[1], need=row[2], offer=row[3], user_id=row[4]) for row in rows]
    
    else:
        result = await db.execute(select(Post).where(Post.user_id == current_user.id))
        posts = result.scalars().all()

    return [PostSchema.model_validate(post, from_attributes=True) for post in posts]