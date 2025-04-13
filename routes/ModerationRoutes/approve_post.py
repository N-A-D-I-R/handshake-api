from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, Post
from app.utils import get_current_superuser, create_notification

router = APIRouter(tags=["Moderation"])

@router.post("/approve/{post_id}", status_code=status.HTTP_201_CREATED, summary="Одобрить пост")
async def approve_post(post_id: int, db: AsyncSession = Depends(get_db), superuser=Depends(get_current_superuser)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    post.status = "approved"
    await db.commit()

    # Получаем автора
    result = await db.execute(select(User).where(User.id == post.user_id))
    author = result.scalars().first()

    # Отправляем уведомление автору на почту
    if author and author.email:
        from app.email import send_email, render_template
        html_body = render_template("post_rejected.html", title=post.title)
        send_email(
            to=author.email,
            subject="Ваш пост отклонён",
            body=html_body,
            html=True
        )
    
    # Создаём уведомление
    await create_notification(author.id, "Пост одобрен", f"Ваш пост «{post.title}» успешно прошёл модерацию.", db)

    return {"message": "Пост одобрен и пользователь уведомлён"}
