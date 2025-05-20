import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import RefreshToken
from app.schemas import TokenResponse
from app.utils import get_jwt_data, bearer_scheme
from app.auth import create_access_token

from datetime import datetime, timedelta, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Users"])

@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK, name="Обновление токена пользователя")
async def refresh(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
):
    jwt_token = credentials.credentials
    data = get_jwt_data(jwt_token, "refresh")

    user_id = data.get("id")
    if not user_id:
        logger.warning("Refresh токен не содержит ID пользователя")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен")

    # Проверка наличия токена в базе
    result = await db.execute(select(RefreshToken).filter(RefreshToken.token == jwt_token))
    db_token = result.scalars().first()

    if not db_token:
        logger.warning("Неверный refresh токен")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный refresh токен")

    # Проверка срока действия
    if db_token.expires_at < datetime.now(timezone.utc):
        await db.delete(db_token)
        await db.commit()
        logger.info("Просроченный refresh токен удалён")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh токен просрочен")

    # Генерация новых токенов
    new_access_token = create_access_token(user_id)

    # Обновление токена в базе
    db_token.token = data
    db_token.expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    await db.commit()

    logger.info(f"Refresh токен успешно обновлён для пользователя ID {user_id}")

    return TokenResponse(
        access_token=new_access_token,
    )