from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.deps import get_current_user_id
from backend.modules.users.schemas import UserRead, UserUpdate
from backend.database.session import get_session
from backend.modules.users.service import UserService


router = APIRouter(prefix="/users", tags=["users"])
service = UserService()


@router.get("/me", response_model=UserRead)
async def get_me(
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    user = await service.get_me(session, user_id)
    return user


@router.patch("/me", response_model=UserRead)
async def update_me(
    payload: UserUpdate,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    user = await service.update_me(session, user_id=user_id, data=payload)
    await session.commit()
    return user
