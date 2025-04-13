from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, EmailConfirmation
from datetime import datetime, timezone
from app.schemas import EmailCodeConfirm

router = APIRouter(tags=["Users"])

@router.post("/verify", response_model=dict, status_code=status.HTTP_202_ACCEPTED, name="Подтверждение пользователя")
async def verify_user(data: EmailCodeConfirm = Query(...), db: AsyncSession = Depends(get_db)):
    email = data.email.strip().lower()  # Нормализуем email

    # Получаем подтверждение
    stmt = select(EmailConfirmation).filter(EmailConfirmation.email == email)
    result = await db.execute(stmt)
    confirmation = result.scalars().first()

    if not confirmation:
        raise HTTPException(status_code=400, detail="Подтверждение не найдено")

    if confirmation.code != data.code:
        raise HTTPException(status_code=400, detail="Неверный код подтверждения")

    if confirmation.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Код подтверждения просрочен")

    # Обновляем статус пользователя
    user_stmt = select(User).filter(User.email == email)
    result = await db.execute(user_stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.is_verified = True

    await db.delete(confirmation)
    await db.commit()

    return {"message": "Пользователь подтверждён и зарегистрирован"}