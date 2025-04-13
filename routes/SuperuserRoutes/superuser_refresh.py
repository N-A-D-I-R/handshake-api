from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import RefreshToken, SuperUser
from app.auth import get_jwt_data, create_access_token
from datetime import datetime, timezone

router = APIRouter(tags=["Superusers"])

@router.post("/refresh", status_code=status.HTTP_201_CREATED, response_model=dict, name="Обновление токена суперпользователя")
async def refresh_superuser_token(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    token = authorization.replace("Bearer ", "")
    payload = get_jwt_data(token, "refresh")

    token_record = await db.execute(select(RefreshToken).where(RefreshToken.token == token, RefreshToken.is_active == True))
    refresh = token_record.scalars().first()

    if not refresh or refresh.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh-токен недействителен или просрочен")

    result = await db.execute(select(SuperUser).where(SuperUser.id == refresh.superuser_id))
    superuser = result.scalars().first()

    if not superuser:
        raise HTTPException(status_code=404, detail="Суперпользователь не найден")

    return {"access_token": create_access_token(superuser.id)}