from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.database import get_db
from app.models import RefreshToken
from app.auth import get_jwt_data
from app.utils import invalidate_access_token

from datetime import datetime, timezone

router = APIRouter(tags=["Superusers"])

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, name="Выход суперпользователя")
async def superuser_logout(
    authorization: str = Header(...),
    x_access_token: str = Header(..., alias="X-Access-Token"),
    db: AsyncSession = Depends(get_db)
):
    refresh_token = authorization.replace("Bearer ", "")
    payload = get_jwt_data(refresh_token, "refresh")

    # 1. Деактивируем refresh
    await db.execute(
        update(RefreshToken).where(RefreshToken.token == refresh_token).values(is_active=False)
    )
    await db.commit()

    # 2. Заблэклистим access
    access_payload = get_jwt_data(x_access_token, "access")
    ttl = int(access_payload["exp"] - datetime.now(timezone.utc).timestamp())
    await invalidate_access_token(x_access_token, ttl)