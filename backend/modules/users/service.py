from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import AuthService
from backend.database.models import User
from backend.modules.users.repository import UserRepository
from backend.modules.users.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, repo: UserRepository | None = None, auth: AuthService | None = None) -> None:
        self.repo = repo or UserRepository()
        self.auth = auth or AuthService()

    async def register(self, session: AsyncSession, data: UserCreate) -> User:
        existing = await self.repo.get_by_email(session, str(data.email))
        if existing:
            raise HTTPException(status_code=409, detail="Пользователь с таким email уже зарегистрирован")

        user = User(
            email=str(data.email),
            password_hash=self.auth.hash_password(data.password),
            role=data.role,
        )

        if data.enterprise_ids:
            from sqlalchemy import select
            from backend.database.models import Enterprise

            stmt = select(Enterprise).where(Enterprise.id.in_(data.enterprise_ids))
            res = await session.execute(stmt)
            enterprises = res.scalars().all()
            user.enterprises.extend(enterprises)

        return await self.repo.create(session, user)

    async def login(self, session: AsyncSession, *, email: str, password: str) -> User:
        user = await self.repo.get_by_email(session, email)
        if not user or not self.auth.verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Неверный email или пароль")
        return user

    async def get_me(self, session: AsyncSession, user_id: int) -> User:
        user = await self.repo.get(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return user

    async def update_me(self, session: AsyncSession, *, user_id: int, data: UserUpdate) -> User:
        user = await self.get_me(session, user_id)

        if data.email is not None:
            user.email = str(data.email)

        password_changed = False
        if data.password is not None:
            if not data.old_password:
                raise HTTPException(status_code=400, detail="Для смены пароля нужен old_password")
            if not self.auth.verify_password(data.old_password, user.password_hash):
                raise HTTPException(status_code=400, detail="old_password неверный")
            user.password_hash = self.auth.hash_password(data.password)
            password_changed = True

        if data.phone is not None:
            user.phone = data.phone

        if password_changed:
            user.token_version += 1

        await session.flush()
        await session.refresh(user)
        return user

    async def revoke_tokens(self, session: AsyncSession, user: User) -> User:
        user.token_version += 1
        await session.flush()
        await session.refresh(user)
        return user
