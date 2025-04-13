from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.database import get_db
from app.models import Post
from app.schemas import PostSchema

router = APIRouter(tags=["Main"])

@router.get("/", response_model=list[PostSchema], status_code=status.HTTP_200_OK, name="Главная страница")
async def get_posts(search: str = Query(..., description="Найти пост"), db: AsyncSession = Depends(get_db)):
    if search:
        result = await db.execute(text("""
            SELECT id, title, need, offer, user_id
            FROM posts
            WHERE search_vector @@ plainto_tsquery('russian', :search)
               OR similarity(title, :search) > 0.2
            ORDER BY ts_rank(search_vector, plainto_tsquery('russian', :search)) DESC,
                     similarity(title, :search) DESC
            LIMIT 10
        """).bindparams(title=search))
        
        rows = result.fetchall()
        posts = [Post(id=row[0], title=row[1], need=row[2], offer=row[3], user_id=row[4]) for row in rows]
    
    else:
        result = await db.execute(select(Post))
        posts = result.scalars().all()

    return [PostSchema.model_validate(post, from_attributes=True) for post in posts]