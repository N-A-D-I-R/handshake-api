import asyncio
from app.models import SuperUser
from app.database import SessionLocal
from passlib.hash import bcrypt

async def create_superuser():
    async with SessionLocal() as session:
        superuser = SuperUser(
            name="Admin",
            username="admin",
            password=bcrypt.hash("admin12345"),
            ip_address="127.0.0.1"
        )
        session.add(superuser)
        await session.commit()
        print("✅ Superuser создан")

asyncio.run(create_superuser())