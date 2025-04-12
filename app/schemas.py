from pydantic import BaseModel, EmailStr, Field
from typing import List

class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="Укажите ваш e-mail")
    name: str = Field(..., min_length=3, max_length=50, description="Ваше имя")
    password: str = Field(..., min_length=8, max_length=50, description="Придумайте пароль")

class EmailCodeConfirm(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, description="Введите код подтверждения")

class UserAuth(BaseModel):
    email: EmailStr = Field(..., description="Введите e-mail")
    password: str = Field(..., min_length=8, max_length=50, description="Введите пароль")

class SuperUserAuth(BaseModel):
    username: str = Field(..., description="Имя суперпользователя")
    password: str = Field(..., min_length=8, max_length=50, description="Пароль суперпользователя")

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class PostBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=50, description="Заголовок поста")
    need: str = Field(..., min_length=3, max_length=1000, description="Что нужно")
    offer: str = Field(..., min_length=3, max_length=1000, description="Что предлагаете")

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