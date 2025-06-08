from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse

from typing import Optional

from app.models import User
from app.schemas import MessageResponse
from app.token import get_token_ttl
from app.dependencies import get_current_user, get_token_from_request
from app.redis import invalidate_access_token, invalidate_refresh_token

router = APIRouter()

@router.post("/logout", response_model=MessageResponse, status_code=status.HTTP_200_OK, name="Выход пользователя")
async def logout_user(
    request: Request, 
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходимо авторизоваться")

    access_token = get_token_from_request(request)
    refresh_token = request.cookies.get("refresh_token")

    access_ttl = get_token_ttl(access_token)
    refresh_ttl = get_token_ttl(refresh_token)

    await invalidate_access_token(access_token, access_ttl)
    await invalidate_refresh_token(refresh_token, refresh_ttl)

    response = JSONResponse(content={"message": "Выход выполнен"})
    response.delete_cookie("refresh_token")

    return response