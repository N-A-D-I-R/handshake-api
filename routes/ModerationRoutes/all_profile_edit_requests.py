from fastapi import APIRouter, Query, Depends, HTTPException, status
from fastapi_pagination import Page, paginate, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.database import get_db
from app.models import ProfileChangeRequest, User
from app.schemas import ProfileChangeOut
from app.dependencies import get_current_user

router = APIRouter()

@router.get(
    "/users-profile-edit/",
    response_model=Page[ProfileChangeOut],
    status_code=status.HTTP_200_OK,
    name="Пользовательские запросы на редактирование профиля"
)
async def get_all_requests(
    search: Optional[str] = Query(default=None, description="Поиск по имени/фамилии/юзернейму"),
    db: AsyncSession = Depends(get_db),
    params: Params = Depends(),
    current_user: Optional[User] = Depends(get_current_user),
):
    if not current_user or not current_user.is_moderator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Страница не найдена")

    if search:
        result = await db.execute(text("""
            SELECT id, user_id, new_username, new_first_name, new_last_name, new_avatar_url, is_approved, created_at
            FROM profile_change_requests
            WHERE is_approved IS NULL
            AND (
                search_vector @@ plainto_tsquery('russian', :search)
                OR similarity(new_username, :search) > 0.2
                OR similarity(new_first_name, :search) > 0.2
                OR similarity(new_last_name, :search) > 0.2
            )
            ORDER BY
                ts_rank(search_vector, plainto_tsquery('russian', :search)) DESC,
                GREATEST(
                    similarity(new_username, :search),
                    similarity(new_first_name, :search),
                    similarity(new_last_name, :search)
                ) DESC
        """).bindparams(search=search))

        rows = result.fetchall()
        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запросов не найдено")

        requests = [
            ProfileChangeOut(
                id=row[0],
                user_id=row[1],
                new_username=row[2],
                new_first_name=row[3],
                new_last_name=row[4],
                new_avatar_url=row[5],
                is_approved=row[6],
                created_at=row[7],
            )
            for row in rows
        ]
        return paginate(requests, params)

    query = select(ProfileChangeRequest).where(ProfileChangeRequest.is_approved.is_(None)).order_by(ProfileChangeRequest.created_at.desc())
    return await sqlalchemy_paginate(db, query, params)