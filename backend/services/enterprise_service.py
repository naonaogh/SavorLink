from __future__ import annotations

from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import Enterprise
from backend.database.schemas.enterprise import EnterpriseCreate, EnterpriseUpdate
from backend.database.repository.enterprise_repository import EnterpriseRepository


class EnterpriseService:
    def __init__(self, repo: EnterpriseRepository | None = None) -> None:
        self.repo = repo or EnterpriseRepository()

    async def list_enterprises(self, session: AsyncSession, *, limit: int = 50, offset: int = 0) -> Sequence[Enterprise]:
        return await self.repo.list(session, limit=limit, offset=offset)

    async def get_enterprise(self, session: AsyncSession, enterprise_id: int) -> Enterprise:
        ent = await self.repo.get(session, enterprise_id)
        if not ent:
            raise HTTPException(status_code=404, detail="Предприятие не найдено")
        return ent

    async def create_enterprise(self, session: AsyncSession, data: EnterpriseCreate) -> Enterprise:
        ent = Enterprise(
            short_name=data.short_name,
            inn=data.inn,
            region=data.region,
            phone=data.phone,
            email=str(data.email) if data.email else None,
        )
        return await self.repo.create(session, ent)

    async def update_enterprise(self, session: AsyncSession, enterprise_id: int, data: EnterpriseUpdate) -> Enterprise:
        ent = await self.get_enterprise(session, enterprise_id)

        if data.short_name is not None:
            ent.short_name = data.short_name
        if data.inn is not None:
            ent.inn = data.inn
        if data.region is not None:
            ent.region = data.region
        if data.phone is not None:
            ent.phone = data.phone
        if data.email is not None:
            ent.email = str(data.email)

        await session.flush()
        await session.refresh(ent)
        return ent

    async def delete_enterprise(self, session: AsyncSession, enterprise_id: int) -> None:
        ent = await self.get_enterprise(session, enterprise_id)
        await self.repo.delete(session, ent)

