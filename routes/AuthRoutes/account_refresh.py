import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.schemas import TokenResponse
from app.utils import get_jwt_data, bearer_scheme
from app.auth import create_access_token, create_refresh_token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Auth"])

@router.get("/account/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK, name="Обновление токена")
async def refresh(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    jwt_token = credentials.credentials
    
    data = get_jwt_data(jwt_token, refresh)

    user_id = data.get("id")
    if not user_id:
        logger.warning("Токен не содержит ID пользователя")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен"
        )
    return {
        "access_token": create_access_token(user_id),
        "refresh_token": create_refresh_token(user_id)
    }