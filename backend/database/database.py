from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
import os
from typing import AsyncGenerator

from .models import Base


# ────────────────────────────────────────────────
#  Получаем DATABASE_URL строго из .env
# ────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()               # ← это ключевая строка

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL не задана в переменных окружения. "
        "Добавьте строку вида:\n"
        "DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname"
    )


# ────────────────────────────────────────────────
#  Движок и сессия
# ────────────────────────────────────────────────

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    pool_pre_ping=True,
    poolclass=NullPool,
    future=True,
)


async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость для FastAPI — получение сессии в эндпоинтах"""
    async with async_session() as session:
        yield session


async def init_db() -> None:
    """Создаёт таблицы (используется обычно при старте приложения или в миграциях)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)