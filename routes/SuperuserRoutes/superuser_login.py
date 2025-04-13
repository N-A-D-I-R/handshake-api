from fastapi import APIRouter, Depends, HTTPException, Request, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import SuperUser
from app.schemas import SuperUserAuth, TokenResponse
from app.auth import create_access_token, create_refresh_token
from app.utils import verify_password

from datetime import datetime, timedelta, timezone

router = APIRouter(tags=["Superusers"])

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK, name="Вход суперпользователя")
async def superuser_login(
    request: Request,
    credentials: SuperUserAuth = Body(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(SuperUser).where(SuperUser.username == credentials.username))
    user = result.scalars().first()

    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    # токен только с ID суперпользователя
    refresh_token = create_refresh_token(user.id)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    return {
        "access_token": create_access_token(user.id),
        "refresh_token": refresh_token
    }