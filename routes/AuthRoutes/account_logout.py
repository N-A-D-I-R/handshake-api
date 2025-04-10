from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import RefreshToken
from app.utils import get_jwt_data, bearer_scheme

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

    # Находим токен в базе данных
    db_token = await db.execute(select(RefreshToken).where(RefreshToken.token == jwt_token))
    db_token = db_token.scalars().first()

    if not db_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh токен не найден")

    # Удаляем токен (или можно пометить его как неактивный)
    await db.delete(db_token)
    await db.commit()

    return {"detail": "Успешно!"}