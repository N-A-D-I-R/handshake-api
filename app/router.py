import jwt
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from fastapi.security import HTTPAuthorizationCredentials

from database import get_db
from app.models import User, Post
from app.schemas import UserAuth, PostSchema, PostCreate, TokenResponse
from app.utils import get_current_user, verify_post_owner, get_jwt_data, bearer_scheme
from app.auth import create_access_token, create_refresh_token, generate_auth_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


# Авторизация
@router.post("/account", response_model=TokenResponse, status_code=status.HTTP_200_OK, name="Авторизация")
async def login(user: UserAuth, db: AsyncSession = Depends(get_db)):
    existing_user = await db.execute(select(User).filter(User.auth_key == user.auth_key))
    user = existing_user.scalars().first()

    if user:
        return {
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
        }
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неправильный номер аккаунта.")
    
# Создание пользователя
@router.get("/account", response_model=dict, status_code=status.HTTP_201_CREATED, name="Создание пользователя")
async def create_user(request: Request, db: AsyncSession = Depends(get_db)):
    ip_address = request.client.host

    existing_users = await db.execute(select(User).filter(User.ip_address == ip_address))
    existing_users = existing_users.scalars().all()

    if len(existing_users) >= 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нельзя использовать более двух аккаунтов на одном IP.")

    auth_key = generate_auth_key()
    new_user = User(auth_key=auth_key, ip_address=ip_address)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"auth_key": new_user.auth_key}

# Обновление токена
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


# Создание поста
@router.post("/posts", response_model=PostSchema, status_code=status.HTTP_201_CREATED, name="Создание поста")
async def create_post(payload: PostCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    post = Post(**payload.model_dump(), user_id=current_user.id)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return PostSchema.model_validate(post)

# Получение списка постов
@router.get("/posts", response_model=list[PostSchema], status_code=status.HTTP_200_OK, name="Неточный поиск")
async def get_posts(title: str = None, db: AsyncSession = Depends(get_db)):
    if title:
        result = await db.execute(text("""
            SELECT id, title, text, user_id
            FROM posts
            WHERE to_tsvector('russian', title) @@ plainto_tsquery('russian', :title)
               OR similarity(title, :title) > 0.2
            ORDER BY ts_rank(to_tsvector('russian', title), plainto_tsquery('russian', :title)) DESC,
                     similarity(title, :title) DESC
            LIMIT 10
        """).bindparams(title=title))
        
        rows = result.fetchall()
        posts = [Post(id=row[0], title=row[1], text=row[2], user_id=row[3]) for row in rows]
    
    else:
        result = await db.execute(select(Post))
        posts = result.scalars().all()

    return [PostSchema.model_validate(post, from_attributes=True) for post in posts]

# Редактирование поста
@router.put("/posts/{id}", response_model=PostSchema, status_code=status.HTTP_200_OK, name="Редактирование поста")
async def edit_post(id: int, payload: PostCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).filter(Post.id == id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")

    verify_post_owner(post, current_user)

    post.text = payload.text
    post.title = payload.title

    await db.commit()
    await db.refresh(post)

    return PostSchema.model_validate(post)

# Удаление поста
@router.delete("/posts/{id}", response_model=PostSchema, status_code=status.HTTP_200_OK, name="Удаление поста")
async def delete_post(id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).filter(Post.id == id))
    post = result.scalars().first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")

    verify_post_owner(post, current_user)

    await db.delete(post)
    await db.commit()

    return PostSchema.model_validate(post)
