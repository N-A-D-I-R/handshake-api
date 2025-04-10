import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import RefreshToken
from app.schemas import TokenResponse
from app.utils import get_jwt_data, bearer_scheme
from app.auth import create_access_token, create_refresh_token

from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Auth"])

@router.get("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK, name="Обновление токена")
async def refresh(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), 
    db: AsyncSession = Depends(get_db)
):
    jwt_token = credentials.credentials
    
    data = get_jwt_data(jwt_token, "refresh")

    user_id = data.get("id")

    if not user_id:
        logger.warning("Токен не содержит ID пользователя")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен"
        )
    
    # Проверяем, существует ли refresh токен в базе данных
    result = await db.execute(
        select(RefreshToken).filter(RefreshToken.token == jwt_token)
    )
    db_token = result.scalars().first()

    if not db_token:
        raise HTTPException(status_code=401, detail="Недействительный refresh токен")
    
    if db_token.expires_at < datetime.now(timezone.utc):
        # Токен просрочен
        await db.delete(db_token)
        await db.commit()
        raise HTTPException(status_code=401, detail="Refresh токен просрочен")

    # Генерируем новые токены
    new_access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)

    # Обновляем refresh токен в БД
    db_token.token = new_refresh_token
    await db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }