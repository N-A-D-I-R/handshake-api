import logging

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import EmailStr
from typing import Optional

from app.models import User
from app.redis import save_email_change
from app.database import get_db
from app.dependencies import get_current_user
from app.email import send_email, render_template
from app.utils import generate_auth_key

logger = logging.getLogger(__name__)
router = APIRouter()

@router.patch("/security/email", status_code=status.HTTP_200_OK, name="Смена почты пользователя")
async def email_change(
    new_email: EmailStr = Form(..., description="Новый email"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходимо авторизоваться")

    new_email = new_email.strip().lower()

    if new_email == current_user.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Этот email уже используется")

    # Проверка, что email не занят
    exists = await db.execute(select(User).filter(User.email == new_email))
    if exists.scalar():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким email уже существует")

    # Генерация и сохранение кода + email в Redis
    code = generate_auth_key()
    await save_email_change(current_user.id, new_email, code)

    # Отправка письма
    html = render_template("confirm_code.html", code=code)
    await send_email(
        to=new_email,
        subject="Подтверждение смены email",
        body=html,
        html=True
    )
    return {"message": "Код подтверждения отправлен на новый email"}