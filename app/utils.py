import string
import random

from sqlalchemy.ext.asyncio import AsyncSession

# Функция для генерации 6-значного кода
def generate_auth_key() -> str:
    return ''.join(random.choices(string.digits, k=6))

# Создание уведомления
async def create_notification(user_id: int, title: str, message: str, db: AsyncSession):
    from app.models import Notification
    notification = Notification(user_id=user_id, title=title, message=message)
    db.add(notification)
    await db.commit()