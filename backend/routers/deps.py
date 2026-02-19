from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.database import get_session
from backend.database.models import User
from backend.database.repository.user_repository import UserRepository


async def get_current_user_id() -> int:
    """
    Заглушка для MVP, пока нет auth.
    Заменить на реальную авторизацию (JWT/session) и доставать user_id из токена.
    """
    return 1


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> User:
    repo = UserRepository()
    user = await repo.get(session, user_id)
    if not user:
        # если в БД нет пользователя 1 — пусть упадёт явно
        raise RuntimeError("MVP stub user not found (id=1). Создайте пользователя или подключите auth.")
    return user

