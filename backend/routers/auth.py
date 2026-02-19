from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.database import get_session
from backend.database.schemas.user import UserCreate, UserRead
from backend.services.user_service import UserService


router = APIRouter(prefix="/auth", tags=["auth"])
service = UserService()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    user: UserRead


@router.post("/register", response_model=UserRead, status_code=201)
async def register(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    user = await service.register(session, payload)
    await session.commit()
    return user


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    user = await service.login(session, email=str(payload.email), password=payload.password)
    # MVP token-заглушка: позже заменить на JWT
    token = f"mvp-token-user-{user.id}"
    return LoginResponse(token=token, user=user)

