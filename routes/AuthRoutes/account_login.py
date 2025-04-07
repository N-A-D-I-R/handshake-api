from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from app.models import User
from app.schemas import UserAuth, TokenResponse
from app.auth import create_access_token, create_refresh_token

router = APIRouter(tags=["Auth"])

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK, name="Вход пользователя")
async def login(user: UserAuth, db: AsyncSession = Depends(get_db)):
    existing_user = await db.execute(select(User).filter(User.auth_key == user.auth_key))
    user = existing_user.scalars().first()

    if user:
        return {
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
        }
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неправильный номер аккаунта.")