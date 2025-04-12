from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, EmailConfirmation
from app.email import send_email
from app.utils import generate_auth_key
from datetime import datetime, timedelta, timezone
from app.schemas import UserRegister

router = APIRouter(tags=["Auth"])

@router.post("/create", response_model=dict, status_code=status.HTTP_201_CREATED, name="Создание пользователя")
async def register_user(request: Request, user: UserRegister = Query(...), db: AsyncSession = Depends(get_db)):
    user_email = user.email.strip().lower()

    existing_user = await db.execute(select(User).filter(User.email == user_email))
    existing = existing_user.scalars().first()

    if existing:
        if existing.is_verified:
            raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
        else:
            # Повторная регистрация — обновляем данные
            existing.name = user.name
            existing.password = user.password
            existing.ip_address = request.client.host
            db_user = existing
    else:
        db_user = User(
            email=user_email,
            name=user.name,
            password=user.password,
            ip_address=request.client.host,
            is_verified=False
        )
        db.add(db_user)

    # Генерация кода подтверждения
    code = generate_auth_key()

    # Ищем или создаём запись подтверждения
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

    send_email(
        to=user_email,
        subject="Код подтверждения",
        body=f"Ваш код подтверждения: {code}"
    )

    return {"message": "Код подтверждения отправлен на почту"}