from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.database import get_session
from backend.database.schemas.enterprise import EnterpriseCreate, EnterpriseRead, EnterpriseUpdate
from backend.services.enterprise_service import EnterpriseService


router = APIRouter(prefix="/enterprises", tags=["enterprises"])
service = EnterpriseService()


@router.get("", response_model=List[EnterpriseRead])
async def list_enterprises(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    ents = await service.list_enterprises(session, limit=limit, offset=offset)
    return ents


@router.get("/{enterprise_id}", response_model=EnterpriseRead)
async def get_enterprise(
    enterprise_id: int,
    session: AsyncSession = Depends(get_session),
):
    ent = await service.get_enterprise(session, enterprise_id)
    return ent


@router.post("", response_model=EnterpriseRead, status_code=201)
async def create_enterprise(
    payload: EnterpriseCreate,
    session: AsyncSession = Depends(get_session),
):
    ent = await service.create_enterprise(session, payload)
    await session.commit()
    return ent


@router.patch("/{enterprise_id}", response_model=EnterpriseRead)
async def update_enterprise(
    enterprise_id: int,
    payload: EnterpriseUpdate,
    session: AsyncSession = Depends(get_session),
):
    ent = await service.update_enterprise(session, enterprise_id, payload)
    await session.commit()
    return ent


@router.delete("/{enterprise_id}", status_code=204)
async def delete_enterprise(
    enterprise_id: int,
    session: AsyncSession = Depends(get_session),
):
    await service.delete_enterprise(session, enterprise_id)
    await session.commit()
    return None

