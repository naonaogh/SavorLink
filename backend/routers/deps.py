from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.database import get_session
from backend.database.models import User
from backend.database.repository.user_repository import UserRepository


async def get_current_user_id(authorization: str | None = Header(None)) -> int:
    """
    Извлекает user_id из токена формата 'Bearer mvp-token-user-{id}'.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Отсутствует заголовок Authorization")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Неверный формат токена")
    
    token = authorization.replace("Bearer ", "")
    prefix = "mvp-token-user-"
    
    if not token.startswith(prefix):
        raise HTTPException(status_code=401, detail="Неверный префикс токена")
    
    try:
        user_id_str = token.replace(prefix, "")
        return int(user_id_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Неверный ID пользователя в токене")


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> User:
    repo = UserRepository()
    user = await repo.get(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

