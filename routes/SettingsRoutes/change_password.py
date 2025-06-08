import logging

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.models import User
from app.schemas import PasswordStr, AuthTokensResponse
from app.database import get_db
from app.token import get_token_ttl
from app.dependencies import get_current_user, get_token_from_request
from app.redis import invalidate_access_token, invalidate_refresh_token
from app.security import hash_password, verify_password
from app.token import create_access_token, create_refresh_token
from app.email import send_email, render_template
from app.utils import create_notification

logger = logging.getLogger(__name__)

router = APIRouter()

@router.patch("/security/password", response_model=AuthTokensResponse, status_code=status.HTTP_200_OK, name="Смена пароля пользователя")
async def change_password(
    request: Request,
    current_password: PasswordStr = Form(..., description="Текущий пароль"),
    new_password: PasswordStr = Form(..., description="Новый пароль"),
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходимо авторизоваться")

    if not verify_password(current_password, current_user.password):
        logger.warning(f"Неверный пароль для email: {current_user.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный пароль")

    current_user.password = hash_password(new_password)
    db.add(current_user)
    await db.commit()

    access_token = get_token_from_request(request)
    refresh_token = request.cookies.get("refresh_token")

    access_ttl = get_token_ttl(access_token)
    refresh_ttl = get_token_ttl(refresh_token)

    await invalidate_access_token(access_token, access_ttl)
    await invalidate_refresh_token(refresh_token, refresh_ttl)

    response = JSONResponse(content={"message": "Выход выполнен"})
    response.delete_cookie("refresh_token")

    html = render_template("change_password.html")
    await send_email(
        to=current_user.email,
        subject="Пароль успешно изменен!",
        body=html,
        html=True
    )
    await create_notification(current_user.id, "Пароль был изменен", "Пароль от вашего аккаунта был успешно изменен!", db)

    return AuthTokensResponse(
        access_token=create_access_token(current_user.id),
        refresh_token=create_refresh_token(current_user.id),
    )