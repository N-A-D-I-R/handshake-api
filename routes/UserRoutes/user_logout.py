from fastapi import APIRouter, Depends, Request, HTTPException, status

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import RefreshToken, User
from app.utils import get_current_user
from app.auth import invalidate_access_token, get_token_from_request

router = APIRouter(tags=["Users"])

@router.post("/logout", status_code=status.HTTP_200_OK, name="Выход пользователя")
async def logout_user(
    request: Request, 
    db: AsyncSession = Depends(get_db), 
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходимо авторизоваться")

    token = get_token_from_request(request)

    await invalidate_access_token(token)

    # Удаляем refresh-токен
    await db.execute(
        RefreshToken.__table__.delete().where(RefreshToken.user_id == current_user.id)
    )
    await db.commit()

    return {"message": "Вы вышли из аккаунта"}