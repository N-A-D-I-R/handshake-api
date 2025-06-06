from fastapi import APIRouter, Depends, Request, HTTPException, status

from typing import Optional

from app.models import User
from app.schemas import MessageResponse
from app.utils import get_current_user
from app.auth import invalidate_access_token, get_token_from_request

router = APIRouter()

@router.post("/logout", response_model=MessageResponse, status_code=status.HTTP_200_OK, name="Выход пользователя")
async def logout_user(
    request: Request, 
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходимо авторизоваться")

    token = get_token_from_request(request)

    await invalidate_access_token(token)

    return {"message": "Вы вышли из аккаунта"}