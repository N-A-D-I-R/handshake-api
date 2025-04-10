from fastapi import APIRouter, Depends, Query, HTTPException, Request, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, RefreshToken
from app.schemas import UserAuth, TokenResponse
from app.auth import create_access_token, create_refresh_token

from datetime import datetime, timedelta, timezone

router = APIRouter(tags=["Auth"])

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK, name="Вход пользователя")
async def login(
    request: Request,
    user: UserAuth = Query(...),
    db: AsyncSession = Depends(get_db)
):
    existing_user = await db.execute(select(User).filter(User.auth_key == user.auth_key))
    user = existing_user.scalars().first()

    if user:
        
        # создаем refresh токен
        refresh_token = create_refresh_token(user.id)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)  # срок действия refresh токена

        # сохраняем refresh токен
        db_token = RefreshToken(
            token=refresh_token,
            user_id=user.id,
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host,
            expires_at=expires_at,
        )

        db.add(db_token)
        await db.commit()

        return {
            "access_token": create_access_token(user.id),
            "refresh_token": refresh_token,
        }
    
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неправильный номер аккаунта.")