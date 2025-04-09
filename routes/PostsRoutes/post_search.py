from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.database import get_db
from app.models import Post
from app.schemas import PostSchema

router = APIRouter(tags=["Posts"])

@router.get("/posts", response_model=list[PostSchema], status_code=status.HTTP_200_OK, name="Неточный поиск")
async def get_posts(title: str = None, db: AsyncSession = Depends(get_db)):
    if title:
        result = await db.execute(text("""
            SELECT id, title, text, user_id
            FROM posts
            WHERE to_tsvector('russian', title) @@ plainto_tsquery('russian', :title)
               OR similarity(title, :title) > 0.2
            ORDER BY ts_rank(to_tsvector('russian', title), plainto_tsquery('russian', :title)) DESC,
                     similarity(title, :title) DESC
            LIMIT 10
        """).bindparams(title=title))
        
        rows = result.fetchall()
        posts = [Post(id=row[0], title=row[1], text=row[2], user_id=row[3]) for row in rows]
    
    else:
        result = await db.execute(select(Post))
        posts = result.scalars().all()

    return [PostSchema.model_validate(post, from_attributes=True) for post in posts]