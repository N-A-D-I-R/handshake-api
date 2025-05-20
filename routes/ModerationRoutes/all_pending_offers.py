from fastapi import APIRouter, Query, Depends, HTTPException, status
from fastapi_pagination import Page, paginate, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from typing import Optional

from app.database import get_db
from app.models import Post, User
from app.utils import get_current_user
from app.schemas import PostSchema

router = APIRouter(tags=["Moderation"])

@router.get("/pending", response_model=Page[PostSchema], status_code=status.HTTP_200_OK, summary="Получить все посты на модерации")
async def get_pending_offers(
    search: Optional[str] = Query(default=None, description="Найти пост"),
    db: AsyncSession = Depends(get_db),
    params: Params = Depends(),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_moderator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Страница не найдена")

    if search:
        result = await db.execute(text("""
            SELECT id, title, need, offer, description, user_id, status
            FROM posts
            WHERE status = 'pending' AND (
                search_vector @@ plainto_tsquery('russian', :search)
                OR similarity(title, :search) > 0.2
            )
            ORDER BY ts_rank(search_vector, plainto_tsquery('russian', :search)) DESC,
                     similarity(title, :search) DESC
        """).bindparams(search=search))

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
                status=[6]
            )
            for row in rows
        ]

        return paginate(posts, params)

    query = select(Post).where(Post.status == "pending")
    return await sqlalchemy_paginate(db, query, params)