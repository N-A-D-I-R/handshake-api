from pydantic import BaseModel, EmailStr, StringConstraints, Field
from typing import List, Optional, Annotated
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

UsernameStr = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=32,
        pattern=r"^[a-zA-Z0-9_]+$"
    )
]

PasswordStr = Annotated[
    str,
    StringConstraints(
        min_length=8,
        max_length=50
    )
]

class UserRegister(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="Укажите ваш e-mail", 
        example=""
    )

    username: UsernameStr = Field(
        ..., 
        description="Придумайте уникальное имя аккаунта", 
        example=""
    )

    password: PasswordStr = Field(
        ..., 
        description="Придумайте пароль (от 8 до 50 символов)", 
        example=""
    )
    
class EmailCodeConfirm(BaseModel):
    email: EmailStr = Field(..., description="E-mail", example="")
    code: str = Field(..., min_length=6, max_length=6, description="Введите код подтверждения", example="")

class UserAuth(BaseModel):
    email: EmailStr = Field(..., description="Введите e-mail", example="")
    password: str = Field(..., min_length=8, max_length=50, description="Введите пароль", example="")

class MessageResponse(BaseModel):
    message: str

class AuthTokensResponse(BaseModel):
    access_token: str
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str

class PostBase(BaseModel):
    avatar_url: str | None = Field(None, min_length=3, max_length=500, description="Фото поста", example="")
    title: str = Field(..., min_length=3, max_length=50, description="Заголовок поста", example="")
    need: str = Field(..., min_length=3, max_length=100, description="Что нужно", example="")
    offer: str = Field(..., min_length=3, max_length=100, description="Что предлагаете", example="")
    description: str = Field(..., min_length=3, max_length=5000, description="Дополнительное описание", example="")

class PostSchema(PostBase):
    id: int
    user_id: int
    
    model_config = {
        "from_attributes": True
    }

class UserProfile(BaseModel):
    id: int
    avatar_url: Optional[str] = None
    username: str
    first_name: str
    last_name: str

class FullUserProfile(UserProfile):
    posts: List[PostSchema] = []
    
    model_config = {
        "from_attributes": True
    }
    
class ProfileChangeCreate(BaseModel):
    new_username: str | None = None
    new_first_name: str | None = None
    new_last_name: str | None = None
    new_avatar_url: str | None = None

class ProfileChangeOut(BaseModel):
    id: int
    user_id: int
    new_username: str | None
    new_first_name: str | None
    new_last_name: str | None
    new_avatar_url: str | None
    created_at: datetime
    is_approved: bool | None

    class Config:
        from_attributes = True

class NotificationSchema(BaseModel):
    id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }