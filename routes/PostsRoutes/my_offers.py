from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi_pagination import Page, paginate, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text

from app.database import get_db
from app.models import User, Post
from app.schemas import PostSchema
from app.utils import get_current_user

router = APIRouter(tags=["Offers"])

@router.get("/my", response_model=Page[PostSchema], status_code=status.HTTP_200_OK, name="Список моих постов")
async def get_my_posts(
    search: str = Query(default=None, description="Найти пост"), 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db), 
    params: Params = Depends(),
):
    if search:
        result = await db.execute(text("""
            SELECT id, title, need, offer, description, user_id, status
            FROM posts
            WHERE user_id = :user_id AND status = 'approved' AND (
                search_vector @@ plainto_tsquery('russian', :search)
                OR similarity(title, :search) > 0.2
            )
            ORDER BY ts_rank(search_vector, plainto_tsquery('russian', :search)) DESC,
                     similarity(title, :search) DESC
        """).bindparams(user_id=current_user.id, search=search))
        
        rows = result.fetchall()
        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Посты не найдены")

        posts = [
            Post(
                id=row[0],
                title=row[1],
                need=row[2],
                offer=row[3],
                description=row[4],
                user_id=row[5],
                status=row[6]
            )
            for row in rows
        ]
        return paginate(posts, params)
    
    query = select(Post).where(Post.status == "approved", Post.user_id == current_user.id)
    return await sqlalchemy_paginate(db, query, params)