from fastapi import APIRouter, Request, Depends, Query, HTTPException, status
from fastapi_pagination import Page, paginate, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from typing import Optional

from app.database import get_db
from app.models import Post
from app.schemas import PostSchema
from app.utils import get_current_user_from_request

router = APIRouter(tags=["Offers"])

@router.get("/search", response_model=Page[PostSchema], status_code=status.HTTP_200_OK, name="Все посты")
async def get_offers(
    request: Request,
    search: Optional[str] = Query(None),
    only_my: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    params: Params = Depends(),
):
    current_user = None

    if only_my:
        try:
            current_user = await get_current_user_from_request(request, db)
        except HTTPException:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходимо авторизоваться")

    if search:
        raw_sql = """
            SELECT id, title, need, offer, user_id, status
            FROM posts
            WHERE status = 'approved'
            {user_filter}
              AND (
                search_vector @@ plainto_tsquery('russian', :search)
                OR similarity(title, :search) > 0.2
              )
            ORDER BY ts_rank(search_vector, plainto_tsquery('russian', :search)) DESC,
                     similarity(title, :search) DESC
        """.format(user_filter="AND user_id = :user_id" if only_my else "")

        params_dict = {"search": search}
        if only_my:
            params_dict["user_id"] = current_user.id

        result = await db.execute(text(raw_sql).bindparams(**params_dict))
        rows = result.fetchall()

        posts = [Post(
            id=row[0], 
            title=row[1], 
            need=row[2], 
            offer=row[3], 
            user_id=row[4], 
            status=row[5]) 
            for row in rows]

        return paginate(posts, params)

    query = select(Post).where(Post.status == "approved")
    if only_my:
        query = query.where(Post.user_id == current_user.id)

    return await sqlalchemy_paginate(db, query, params)