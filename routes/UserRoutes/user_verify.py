from fastapi import APIRouter, Depends, Form, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, EmailConfirmation
from app.utils import create_notification
from app.email import send_email, render_template
from app.schemas import EmailCodeConfirm, MessageResponse

from datetime import datetime, timezone

router = APIRouter(tags=["Users"])

@router.post("/verify", response_model=MessageResponse, status_code=status.HTTP_202_ACCEPTED, name="Подтверждение пользователя")
async def verify_user(
    data: EmailCodeConfirm = Form(...), 
    db: AsyncSession = Depends(get_db)
):
    email = data.email.strip().lower()

    # Получаем подтверждение
    stmt = select(EmailConfirmation).filter(EmailConfirmation.email == email)
    result = await db.execute(stmt)
    confirmation = result.scalars().first()

    if not confirmation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Подтверждение не найдено")

    if confirmation.code != data.code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный код подтверждения")

    if confirmation.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Код подтверждения просрочен")

    # Обновляем статус пользователя
    user_stmt = select(User).filter(User.email == email)
    result = await db.execute(user_stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    user.is_verified = True

    await db.delete(confirmation)
    await db.commit()

    # Отправляем уведомление на почту
    html = render_template("account_verified.html", name=user.name)
    await send_email(
        to=user.email,
        subject="Ваш аккаунт подтверждён!",
        body=html,
        html=True
    )

    # Создаём уведомление в системе
    await create_notification(user.id, "Аккаунт подтверждён", "Ваш аккаунт успешно подтверждён!", db)

    return {"message": "Пользователь подтверждён и зарегистрирован"}