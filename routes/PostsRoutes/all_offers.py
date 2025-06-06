from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi_pagination import Page, paginate, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional

from app.database import get_db
from app.models import Post, User
from app.schemas import PostSchema
from app.utils import get_current_user

router = APIRouter()

@router.get("/", response_model=Page[PostSchema], status_code=status.HTTP_200_OK, name="Все посты")
async def get_offers(
    search: Optional[str] = Query(default=None, description="Найти пост"),
    only_my: bool = Query(default=False, description="Только мои посты"),
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    params: Params = Depends(),
):
    if only_my and not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходимо авторизоваться")

    if search:
        user_filter = "AND user_id = :user_id" if only_my else ""
        query_str = f"""
            SELECT id, title, need, offer, description, user_id, status
            FROM posts
            WHERE status = 'approved'
              {user_filter}
              AND (
                search_vector @@ plainto_tsquery('russian', :search)
                OR similarity(title, :search) > 0.2
              )
            ORDER BY ts_rank(search_vector, plainto_tsquery('russian', :search)) DESC,
                     similarity(title, :search) DESC
        """
        params_dict = {"search": search}
        if only_my:
            params_dict["user_id"] = current_user.id

        result = await db.execute(text(query_str).bindparams(**params_dict))
        rows = result.fetchall()

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

    query = select(Post).where(Post.status == "approved")
    if only_my and current_user:
        query = query.where(Post.user_id == current_user.id)

    return await sqlalchemy_paginate(db, query, params)