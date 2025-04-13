from fastapi import APIRouter, Depends, Request, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import RefreshToken
from app.utils import get_current_superuser
from app.auth import invalidate_access_token, get_token_from_request

router = APIRouter(tags=["Superusers"])

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, name="Выход суперпользователя")
async def logout_user(request: Request, db: AsyncSession = Depends(get_db), current_superuser=Depends(get_current_superuser)):
    token = get_token_from_request(request)

    await invalidate_access_token(token)

    # Удаляем refresh-токен
    await db.execute(
        RefreshToken.__table__.delete().where(RefreshToken.superuser_id == current_superuser.id)
    )
    await db.commit()

    return {"message": "Вы вышли из аккаунта"}