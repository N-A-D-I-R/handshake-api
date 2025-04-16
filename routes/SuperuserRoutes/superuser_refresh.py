import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import RefreshToken
from app.auth import get_jwt_data, create_access_token, create_refresh_token
from app.utils import bearer_scheme

from datetime import datetime, timezone

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Superusers"])

@router.get("/refresh", status_code=status.HTTP_201_CREATED, response_model=dict, name="Обновление токена суперпользователя")
async def refresh(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), 
    db: AsyncSession = Depends(get_db)
):
    jwt_token = credentials.credentials
    
    data = get_jwt_data(jwt_token, "refresh")

    user_id = data.get("id")

    if not user_id:
        logger.debug("Токен не содержит ID пользователя")
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
        logger.debug("Недействительный refresh токен")
        raise HTTPException(status_code=401, detail="Недействительный refresh токен")
    
    if db_token.expires_at < datetime.now(timezone.utc):
        # Токен просрочен
        await db.delete(db_token)
        await db.commit()

        logger.debug("Refresh токен просрочен")
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