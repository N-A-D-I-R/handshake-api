from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, Post
from app.schemas import PostSchema
from app.utils import get_current_user, verify_post_owner, create_notification

router = APIRouter(tags=["Offers"])

@router.delete("/{id}", response_model=PostSchema, status_code=status.HTTP_200_OK, name="Удаление поста")
async def delete_post(
    id: int, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Post).filter(Post.id == id))
    post = result.scalars().first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")

    result = await db.execute(select(User).where(User.id == post.user_id))
    author = result.scalars().first()
    
    if not current_user.is_moderator or author.is_moderator:
        verify_post_owner(post, current_user)

    await db.delete(post)
    await db.commit()

    if author and author.email:
        from app.email import send_email, render_template
        html_body = render_template("post_approved.html", title=post.title)
        await send_email(
            to=author.email,
            subject="Ваш пост отклонён",
            body=html_body,
            html=True
        )

    if current_user.is_moderator and current_user.id != author.id:
        await create_notification(author.id, "Пост был удален модератором", f"Ваш пост «{post.title}» был удален.", db)
    else:
        await create_notification(author.id, "Пост удален", f"Ваш пост «{post.title}» был удален.", db)

    return PostSchema.model_validate(post)