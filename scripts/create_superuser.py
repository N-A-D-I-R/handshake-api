import asyncio
from app.models import SuperUser
from app.database import SessionLocal
from passlib.hash import bcrypt

async def create_superuser():
    name = input("Введите имя: ").strip()
    username = input("Введите логин: ").strip()
    password = input("Введите пароль: ").strip()
    ip_address = "none"

    async with SessionLocal() as session:
        superuser = SuperUser(
            name=name,
            username=username,
            password=bcrypt.hash(password),
            ip_address=ip_address
        )
        session.add(superuser)
        await session.commit()
        print(f"✅ Суперпользователь '{username}' создан успешно!")

if __name__ == "__main__":
    asyncio.run(create_superuser())