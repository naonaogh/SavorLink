from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.database import get_session
from backend.database.schemas.product import ProductShort
from backend.routers.deps import get_current_user_id
from backend.services.favorite_service import FavoriteService

router = APIRouter(prefix="/favorites", tags=["favorites"])
service = FavoriteService()

@router.get("/products", response_model=List[ProductShort])
async def list_favorite_products(
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    return await service.list_favorite_products(session, user_id=user_id)

@router.post("/products/{product_id}", status_code=status.HTTP_201_CREATED)
async def add_favorite_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    await service.add_favorite_product(session, user_id=user_id, product_id=product_id)
    await session.commit()
    return {"status": "ok"}

@router.delete("/products/{product_id}")
async def remove_favorite_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    await service.remove_favorite_product(session, user_id=user_id, product_id=product_id)
    await session.commit()
    return {"status": "ok"}
