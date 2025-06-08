from fastapi import APIRouter, Depends, HTTPException, status

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, Post
from app.schemas import MessageResponse
from app.dependencies import get_current_user
from app.utils import create_notification

router = APIRouter()

@router.post("/posts/{post_id}/reject", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, summary="Отклонить и удалить пост")
async def reject_post(
    post_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user or not current_user.is_moderator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Страница не найдена")

    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")

    # Получаем email пользователя до удаления
    result = await db.execute(select(User).where(User.id == post.user_id))
    author = result.scalars().first()

    await db.delete(post)
    await db.commit()

    # Отправляем уведомление автору на почту
    if author and author.email:
        from app.email import send_email, render_template
        html_body = render_template("post_rejected.html", title=post.title)
        await send_email(
            to=author.email,
            subject="Ваш пост отклонён",
            body=html_body,
            html=True
        )
    
    # Создаём уведомление
    await create_notification(author.id, "Пост отклонён", f"Пост «{post.title}» не прошёл модерацию и был удалён.", db)

    return {"message": "Пост отклонён и удалён. Автор уведомлён."}