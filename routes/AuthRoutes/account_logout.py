from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import RefreshToken
from app.utils import get_jwt_data, get_redis_connection, invalidate_access_token, bearer_scheme

router = APIRouter(tags=["Auth"])

@router.post("/logout", status_code=status.HTTP_200_OK, name="Выход пользователя")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
):
    jwt_token = credentials.credentials

    # Пытаемся получить данные из токена
    data = get_jwt_data(jwt_token, "refresh")

    # Проверяем наличие ID пользователя в токене
    user_id = data.get("id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен")

    try:

        # Находим refresh токен в базе данных
        db_refresh_token = await db.execute(select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.is_active == True))
        db_refresh_token = db_refresh_token.scalars().first()

        if db_refresh_token:
            # Помечаем токен как неактивный
            db_refresh_token.is_active = False
            await db.commit()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refresh токен не найден")

        # Инвалидируем access token (добавляем в черный список)
        await invalidate_access_token(jwt_token)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return {"detail": "Успешно!"}