import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, EmailConfirmation
from app.email import send_email, render_template
from app.utils import generate_auth_key, hash_password
from datetime import datetime, timedelta, timezone
from app.schemas import UserRegister, MessageResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Users"])

@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, name="Регистрация пользователя")
async def register_user(
    request: Request, 
    user: UserRegister = Form(...), 
    db: AsyncSession = Depends(get_db)
):
    user_email = user.email.strip().lower()

    existing_user = await db.execute(select(User).filter(User.email == user_email))
    existing = existing_user.scalars().first()

    if existing:
        if existing.is_verified:
            logger.info("Email уже зарегистрирован")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email уже зарегистрирован")
        else:
            logger.info("Повторная регистрация")

            # Повторная регистрация — обновляем данные
            existing.name = user.name
            existing.password = hash_password(user.password)
            existing.ip_address = request.client.host
            db_user = existing
    else:
        db_user = User(
            email=user_email,
            name=user.name,
            password=hash_password(user.password),
            ip_address=request.client.host,
            is_verified=False,
            is_moderator=False
        )
        db.add(db_user)

    # Генерация кода подтверждения
    logger.info("Генерируем код подтверждения")
    code = generate_auth_key()
    logger.info("Код сгенерирован успешно")

    # Ищем или создаём запись подтверждения
    logger.info("Ищем или создаём запись подтверждения")
    conf_stmt = select(EmailConfirmation).filter(EmailConfirmation.email == user_email)
    result = await db.execute(conf_stmt)
    confirmation = result.scalars().first()

    if confirmation:
        confirmation.code = code
        confirmation.expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    else:
        confirmation = EmailConfirmation(
            email=user_email,
            code=code,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
        )
        db.add(confirmation)

    await db.commit()
    logger.info("Успешно")

    logger.info("Создаем шаблон для сообщения")
    html_body = render_template("confirm_code.html", code=code)
    logger.info("Шаблон успешно создан")

    logger.info("Отправляем сообщение")
    await send_email(
        to=user_email,
        subject="Код подтверждения",
        body=html_body,
        html=True
    )

    return {"message": "Код подтверждения отправлен на почту"}