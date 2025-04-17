import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, RefreshToken
from app.schemas import UserAuth, TokenResponse
from app.auth import create_access_token, create_refresh_token
from app.utils import verify_password, create_notification
from app.email import send_email, render_template

from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Users"])

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK, name="Вход пользователя")
async def login(
    request: Request,
    user_data: UserAuth = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalars().first()

    if not user or not user.is_verified:
        logger.warning(f"Попытка входа с несуществующим или неподтвержденным email: {user_data.email}")
        raise HTTPException(status_code=401, detail="Пользователь не найден или не подтвержден")

    if not verify_password(user_data.password, user.password):
        logger.warning(f"Неверный пароль для email: {user_data.email}")
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    # создаем refresh токен
    refresh_token = create_refresh_token(user.id)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    db_token = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host,
        expires_at=expires_at,
    )

    db.add(db_token)
    await db.commit()

    # Дата/время + IP + User-Agent
    ip = request.client.host
    ua = request.headers.get("user-agent", "Неизвестно")
    dt = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M:%S %Z")

    html_body = render_template("login_alert.html", datetime=dt, ip=ip, user_agent=ua)

    send_email(
        to=user.email,
        subject="Вход в аккаунт",
        body=html_body,
        html=True
    )

    # Отправляем уведомление пользователю
    await create_notification(user.id, "Вход в аккаунт", f"Вы вошли в аккаунт с IP {request.client.host}", db)

    return {
        "access_token": create_access_token(user.id),
        "refresh_token": refresh_token
    }