import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.redis import add_verification_code
from app.email import send_email, render_template
from app.security import hash_password
from app.utils import generate_auth_key
from app.models import User
from app.schemas import UserRegister, MessageResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, name="Регистрация пользователя")
async def register_user(
    request: Request, 
    user: UserRegister = Form(...), 
    db: AsyncSession = Depends(get_db)
):
    # Проверка на существующий username и email
    existing_username_query = await db.execute(select(User).filter(User.username == user.username.strip().lower()))
    existing_username = existing_username_query.scalars().first()
    if existing_username:
        logger.info("Username уже занят")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username уже занят"
        )

    existing_email_query = await db.execute(select(User).filter(User.email == user.email.strip().lower()))
    existing_email = existing_email_query.scalars().first()
    if existing_email:
        logger.info("Email уже занят")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email уже занят"
        )
    
    db_user = User(
        email=user.email.strip().lower(),
        username=user.username,
        password=hash_password(user.password),
        ip_address=request.client.host,
        is_verified=False,
        is_moderator=False
    )
    db.add(db_user)
    await db.commit()

    # Генерация кода подтверждения
    logger.info("Генерируем код подтверждения")
    code = generate_auth_key()
    await add_verification_code(email=db_user.email, code=code,)
    logger.info("Код сгенерирован успешно")

    # Отправка кода подтверждения на почту
    logger.info("Создаем шаблон для сообщения")
    html_body = render_template("confirm_code.html", code=code)

    try:
        logger.info("Отправляем сообщение")
        await send_email(
            to=user.email,
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