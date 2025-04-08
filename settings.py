import os

# JWT
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# База данных
POSTGRESQL_DATABASE_URL = os.getenv(
    "POSTGRESQL_DATABASE_URL",
    "postgresql+asyncpg://crutoi:qwerty123@localhost:5432/startupproject_db"
)

# Debug режим
DEBUG = os.getenv("DEBUG", "True") == "True"