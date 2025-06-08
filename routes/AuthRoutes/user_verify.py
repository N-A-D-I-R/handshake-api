from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.token import create_access_token, create_refresh_token, get_token_ttl
from app.redis import check_verification_code, get_redis_connection
from app.redis import invalidate_access_token, invalidate_refresh_token
from app.dependencies import get_token_from_request
from app.security import hash_password
from app.utils import create_notification
from app.email import send_email, render_template
from app.models import User
from app.schemas import EmailStr, PasswordStr, AuthTokensResponse, ConfirmationTarget

router = APIRouter()

@router.post("/verify", response_model=AuthTokensResponse, status_code=status.HTTP_202_ACCEPTED, name="Подтверждение пользователя")
async def verify_user(
    request: Request,
    email: EmailStr = Form(..., description="E-mail"),
    code: str = Form(..., min_length=6, max_length=6, description="Введите код подтверждения"),
    new_password: Optional[PasswordStr] = Form(None, description="Введите новый пароль"),
    target: ConfirmationTarget = Form(..., description="Цель подтверждения"),
    db: AsyncSession = Depends(get_db)
):
    email = email.strip().lower()    
    user_stmt = select(User).filter(User.email == email)
    result = await db.execute(user_stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    match target:
        case ConfirmationTarget.rescue:
            await check_verification_code(email, code)

            if not new_password:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="При восстановлении аккаунта требуется новый пароль"
                )
            
            user.password = hash_password(new_password)
            html = render_template("reset_account.html")
            await send_email(
                to=user.email,
                subject="Ваш аккаунт восстановлен!",
                body=html,
                html=True
            )

            await create_notification(user.id, "Аккаунт восстановлен", "Ваш аккаунт был успешно восстановлен!", db)
        case ConfirmationTarget.verification:
            await check_verification_code(email, code)

            user.is_verified = True
            html = render_template("account_verified.html")
            await send_email(
                to=user.email,
                subject="Ваш аккаунт подтверждён!",
                body=html,
                html=True
            )

            await create_notification(user.id, "Аккаунт подтверждён", "Ваш аккаунт успешно подтверждён!", db)
        case ConfirmationTarget.change_email:
            user_stmt = select(User).filter(User.email == email)
            result = await db.execute(user_stmt)
            user = result.scalars().first()

            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

            redis = await get_redis_connection()
            redis_key_email = f"email_change:{user.id}"
            new_email = await redis.get(redis_key_email)

            if not new_email:
                await redis.close()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Срок действия кода истёк")

            redis_key_code = f"email_code:{new_email}"
            stored_code = await redis.get(redis_key_code)

            if stored_code != code:
                await redis.close()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный код подтверждения")

            await redis.delete(redis_key_email)
            await redis.delete(redis_key_code)
            await redis.close()

            user.email = new_email

            access_token = get_token_from_request(request)
            refresh_token = request.cookies.get("refresh_token")

            access_ttl = get_token_ttl(access_token)
            refresh_ttl = get_token_ttl(refresh_token)

            await invalidate_access_token(access_token, access_ttl)
            await invalidate_refresh_token(refresh_token, refresh_ttl)

            response = JSONResponse(content={"message": "Выход выполнен"})
            response.delete_cookie("refresh_token")

            html = render_template("email_changed.html", new_email=new_email)
            await send_email(
                to=new_email,
                subject="Ваш email был изменён",
                body=html,
                html=True
            )
            await create_notification(user.id, "Email обновлён", f"Ваш email был изменён на {new_email}", db)
            
        case _:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверная цель подтверждения")

    await db.commit()

    return AuthTokensResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )