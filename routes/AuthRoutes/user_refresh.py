import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.schemas import RefreshTokenResponse
from app.dependencies import get_jwt_data, bearer_scheme
from app.token import create_access_token

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/refresh", response_model=RefreshTokenResponse, status_code=status.HTTP_200_OK, name="Обновление токена пользователя")
async def refresh(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    jwt_token = credentials.credentials
    data = get_jwt_data(jwt_token, "refresh")

    user_id = data.get("id")
    if not user_id:
        logger.warning("Refresh токен не содержит ID пользователя")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен")

    new_access_token = create_access_token(user_id)

    logger.info(f"Refresh токен успешно обновлён для пользователя ID {user_id}")

    return RefreshTokenResponse(
        access_token=new_access_token,
    )