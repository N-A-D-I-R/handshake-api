from fastapi import APIRouter, Query, Depends, HTTPException, status
from fastapi_pagination import Page, paginate, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from typing import Optional

from app.database import get_db
from app.models import User
from app.schemas import UserProfile

router = APIRouter()

@router.get("/find", response_model=Page[UserProfile], status_code=status.HTTP_200_OK, name="Поиск пользователей")
async def find_user(
    search: Optional[str] = Query(default=None, description="Найти пользователя по username, имени или фамилии"),
    params: Params = Depends(),
    db: AsyncSession = Depends(get_db)
):
    if search:
        result = await db.execute(text("""
            SELECT id, username, first_name, last_name, avatar_url
            FROM users
            WHERE is_verified = true AND (
                search_vector @@ plainto_tsquery('russian', :search)
                OR similarity(username, :search) > 0.2
                OR similarity(first_name, :search) > 0.2
                OR similarity(last_name, :search) > 0.2
            )
            ORDER BY ts_rank(search_vector, plainto_tsquery('russian', :search)) DESC,
                     similarity(username, :search) DESC
        """).bindparams(search=search))

        rows = result.fetchall()
        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователи не найдены")

        users = [
            UserProfile(
                id=row[0],
                username=row[1],
                first_name=row[2],
                last_name=row[3],
                avatar_url=row[4]
            )
            for row in rows
        ]
        return paginate(users, params)

    query = select(User).where(User.is_verified == True)
    return await sqlalchemy_paginate(db, query, params)