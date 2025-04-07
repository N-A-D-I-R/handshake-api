from pydantic import BaseModel
from typing import List

class UserAuth(BaseModel):
    auth_key: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class PostBase(BaseModel):
    title: str
    text: str

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