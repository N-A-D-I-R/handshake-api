from pydantic import BaseModel, EmailStr, Field
from typing import List
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="Укажите ваш e-mail", example="")
    name: str = Field(..., min_length=3, max_length=50, description="Ваше имя", example="")
    password: str = Field(..., min_length=8, max_length=50, description="Придумайте пароль", example="")
    
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
    title: str = Field(..., min_length=3, max_length=50, description="Заголовок поста", example="")
    need: str = Field(..., min_length=3, max_length=100, description="Что нужно", example="")
    offer: str = Field(..., min_length=3, max_length=100, description="Что предлагаете", example="")
    description: str = Field(..., min_length=3, max_length=5000, description="Дополнительное описание", example="")

class PostCreate(PostBase):
    pass

class PostSchema(PostBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

class UserSchema(BaseModel):
    id: int
    auth_key: str
    ip_address: str
    posts: List[PostSchema] = []
    
    class Config:
        from_attributes = True

class NotificationSchema(BaseModel):
    id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True