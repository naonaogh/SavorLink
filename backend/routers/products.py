from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.database import get_session
from backend.database.schemas.product import ProductCreate, ProductRead, ProductShort, ProductUpdate
from backend.services.product_service import ProductService


router = APIRouter(prefix="/products", tags=["products"])
service = ProductService()


@router.get("", response_model=List[ProductShort])
async def list_products(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    products = await service.list_products(session, limit=limit, offset=offset)
    return products


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
):
    product = await service.get_product(session, product_id)
    return product


@router.post("", response_model=ProductRead, status_code=201)
async def create_product(
    payload: ProductCreate,
    session: AsyncSession = Depends(get_session),
):
    # TODO: заменить на enterprise_id из auth-контекста
    product = await service.create_product(session, payload, enterprise_id=1)
    await session.commit()
    return product


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    session: AsyncSession = Depends(get_session),
):
    product = await service.update_product(session, product_id, payload)
    await session.commit()
    return product


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
):
    await service.delete_product(session, product_id)
    await session.commit()
    return None

