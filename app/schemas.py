from pydantic import BaseModel, Field
from typing import List

class UserAuth(BaseModel):
    auth_key: str = Field(..., min_length=16, max_length=16, description="Ключ авторизации пользователя")

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