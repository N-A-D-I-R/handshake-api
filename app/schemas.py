from enum import Enum
from datetime import datetime
from typing import List, Optional, Annotated

from pydantic import Field, PrivateAttr, computed_field
from pydantic import BaseModel, EmailStr, StringConstraints

class ConfirmationTarget(str, Enum):
    rescue = "rescue"
    verification = "verification"
    change_email = "change_email"

UsernameStr = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=32,
        pattern=r"^[a-z0-9_]+$"
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
    email: EmailStr = Field(..., description="Укажите ваш e-mail")
    username: UsernameStr = Field(..., description="Придумайте уникальное имя аккаунта")
    password: PasswordStr = Field(..., description="Придумайте пароль (от 8 до 50 символов)")
    
class UserAuth(BaseModel):
    email: EmailStr = Field(..., description="Введите e-mail")
    password: str = Field(..., min_length=8, max_length=50, description="Введите пароль")

class MessageResponse(BaseModel):
    message: str

class AuthTokensResponse(BaseModel):
    access_token: str
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str

class PostBase(BaseModel):
    avatar_url: str | None = Field(None, min_length=3, max_length=500, description="Фото поста")
    title: str = Field(..., min_length=3, max_length=50, description="Заголовок поста")
    need: str = Field(..., min_length=3, max_length=100, description="Что нужно")
    offer: str = Field(..., min_length=3, max_length=100, description="Что предлагаете")
    description: str = Field(..., min_length=3, max_length=5000, description="Дополнительное описание")

class PostSchema(PostBase):
    id: int
    user_id: int
    
    model_config = {
        "from_attributes": True
    }

class UserProfile(BaseModel):
    id: int
    avatar_url: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class FullUserProfile(UserProfile):
    posts: List[PostSchema] = []
    
    model_config = {
        "from_attributes": True
    }

class UserMe(UserProfile):
    posts: List[PostSchema] = []

    # приватный флаг, не попадает в JSON
    _is_moderator: bool = PrivateAttr()

    model_config = {
        "from_attributes": True
    }

    def __init__(self, **data):
        # Вытаскиваем is_moderator из входных данных и убираем его из kwargs
        is_moderator = data.pop("is_moderator", False)
        super().__init__(**data)
        self._is_moderator = is_moderator

    @computed_field
    @property
    def role(self) -> str:
        return "moderator" if self._is_moderator else "user"
    
class ProfileChangeCreate(BaseModel):
    new_username: str | None = Field(None, min_length=3, max_length=32, description="Username")
    new_first_name: str | None = Field(None, min_length=3, max_length=50, description="Имя")
    new_last_name: str | None = Field(None, min_length=3, max_length=50, description="Фамилия")
    new_avatar_url: str | None = Field(None, min_length=3, max_length=500, description="Фото")

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