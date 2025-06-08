import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.schemas import UserAuth, AuthTokensResponse
from app.token import create_access_token, create_refresh_token
from app.security import verify_password
from app.utils import create_notification
from app.email import send_email, render_template

from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login", response_model=AuthTokensResponse, status_code=status.HTTP_200_OK, name="Вход пользователя")
async def login(
    request: Request,
    user_data: UserAuth = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalars().first()

    if not user or not user.is_verified:
        logger.warning(f"Попытка входа с несуществующим или неподтвержденным email: {user_data.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден или не подтвержден")

    if not verify_password(user_data.password, user.password):
        logger.warning(f"Неверный пароль для email: {user_data.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")

    # Дата/время + IP + User-Agent
    ip = request.client.host
    ua = request.headers.get("user-agent", "Неизвестно")
    dt = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M:%S %Z")

    html_body = render_template("login_alert.html", datetime=dt, ip=ip, user_agent=ua)

    await send_email(
        to=user.email,
        subject="Вход в аккаунт",
        body=html_body,
        html=True
    )

    # Отправляем уведомление пользователю
    await create_notification(user.id, "Вход в аккаунт", f"Вы вошли в аккаунт с IP {request.client.host}", db)

    return AuthTokensResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )