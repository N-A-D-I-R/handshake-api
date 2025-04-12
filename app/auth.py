import jwt
import logging

from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone

import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

logger = logging.getLogger(__name__)

# Функции создания токенов
def create_token(user_id: int, token_type: str, lifetime: timedelta):
    payload = {
        "id": user_id,
        "type": token_type,
        "exp": datetime.now(timezone.utc) + lifetime
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_access_token(user_id: int):
    return create_token(user_id, token_type="access", lifetime=timedelta(minutes=15))


def create_refresh_token(user_id: int):
    return create_token(user_id, token_type="refresh", lifetime=timedelta(days=7))


def get_jwt_data(jwt_token: str, token_type: str):
    try:
        data = jwt.decode(jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        logger.warning("Токен истек")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия токена истек"
        )
    except jwt.DecodeError:
        logger.warning("Некорректный токен")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен"
        )

    if data.get("type") != token_type:
        logger.warning("Попытка использовать токен неверного типа")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный тип токена"
        )
    return data