import logging

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User
from app.schemas import EmailStr
from app.database import get_db
from app.utils import generate_auth_key
from app.redis import add_verification_code
from app.email import send_email, render_template

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/reset", status_code=status.HTTP_200_OK, name="Восстановление аккаунта пользователя")
async def reset_password(
    email: EmailStr = Form(..., description="E-mail"),
    db: AsyncSession = Depends(get_db)
):
    email = email.strip().lower()
    
    # Проверяем, есть ли пользователь с таким email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь с таким email не найден")

    # Генерация кода подтверждения
    logger.info("Генерируем код подтверждения")
    code = generate_auth_key()
    await add_verification_code(email=email, code=code,)
    logger.info("Код сгенерирован успешно")

    # Отправка кода подтверждения на почту
    logger.info("Создаем шаблон для сообщения")
    html_body = render_template("confirm_code.html", code=code)

    try:
        logger.info("Отправляем сообщение")
        await send_email(
            to=email,
            subject="Код подтверждения",
            body=html_body,
            html=True
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке письма: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось отправить код подтверждения на почту"
        )

    return {"message": "Код подтверждения отправлен на почту"}