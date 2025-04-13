from fastapi import APIRouter, Depends, HTTPException, Request, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import SuperUser, RefreshToken
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
    superuser = result.scalars().first()

    if not superuser or not verify_password(credentials.password, superuser.password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    access_token = create_access_token(superuser.id)
    refresh_token = create_refresh_token(superuser.id)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    db_token = RefreshToken(
        token=refresh_token,
        superuser_id=superuser.id,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host,
        expires_at=expires_at,
    )

    db.add(db_token)
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }