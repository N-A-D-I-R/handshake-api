from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from app.models import User
from app.auth import generate_auth_key

router = APIRouter(tags=["Auth"])

@router.get("/create", response_model=dict, status_code=status.HTTP_201_CREATED, name="Создание пользователя")
async def create_user(request: Request, db: AsyncSession = Depends(get_db)):
    ip_address = request.client.host

    existing_users = await db.execute(select(User).filter(User.ip_address == ip_address))
    existing_users = existing_users.scalars().all()

    if len(existing_users) >= 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нельзя использовать более двух аккаунтов на одном IP.")

    auth_key = generate_auth_key()
    new_user = User(auth_key=auth_key, ip_address=ip_address)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"auth_key": new_user.auth_key}