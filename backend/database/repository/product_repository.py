from __future__ import annotations
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database.models import Product


class ProductRepository:
    async def list(self, session: AsyncSession, *, limit: int = 50, offset: int = 0) -> Sequence[Product]:
        stmt = (
            select(Product)
            .options(
                selectinload(Product.enterprise),
                selectinload(Product.category),
            )
            .limit(limit)
            .offset(offset)
            .order_by(Product.id.desc())
        )
        res = await session.execute(stmt)
        return res.scalars().all()

    async def get(self, session: AsyncSession, product_id: int) -> Product | None:
        stmt = (
            select(Product)
            .where(Product.id == product_id)
            .options(
                selectinload(Product.enterprise),
                selectinload(Product.category),
            )
        )
        res = await session.execute(stmt)
        return res.scalars().first()

    async def create(self, session: AsyncSession, product: Product) -> Product:
        session.add(product)
        await session.flush()
        # подгружаем отношения для безопасной сериализации
        await session.refresh(product)
        return product

    async def delete(self, session: AsyncSession, product: Product) -> None:
        await session.delete(product)