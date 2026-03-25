from __future__ import annotations
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.database.models import Product
from backend.database.schemas.product import ProductCreate, ProductUpdate
from backend.database.repository.product_repository import ProductRepository


class ProductService:
    def __init__(self, repo: ProductRepository | None = None) -> None:
        self.repo = repo or ProductRepository()

    async def list_products(self, session: AsyncSession, *, limit: int = 50, offset: int = 0) -> Sequence[Product]:
        return await self.repo.list(session, limit=limit, offset=offset)

    async def get_product(self, session: AsyncSession, product_id: int) -> Product:
        product = await self.repo.get(session, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")
        return product

    async def create_product(self, session: AsyncSession, data: ProductCreate, *, enterprise_id: int) -> Product:
        product = Product(
            name=data.name,
            description=data.description,
            price=data.price,
            min_order_qty=data.min_order_qty,
            quantity_in_stock=data.quantity_in_stock,
            enterprise_id=enterprise_id,
            category_id=data.category_id,
        )
        await self.repo.create(session, product)

        # подгружаем отношения для сериализации
        stmt = (
            select(Product)
            .where(Product.id == product.id)
            .options(
                selectinload(Product.category),
                selectinload(Product.enterprise),
            )
        )
        res = await session.execute(stmt)
        return res.scalar_one()

    async def update_product(self, session: AsyncSession, product_id: int, data: ProductUpdate) -> Product:
        product = await self.get_product(session, product_id)

        for field in ["name", "description", "price", "min_order_qty", "quantity_in_stock", "category_id"]:
            value = getattr(data, field)
            if value is not None:
                setattr(product, field, value)

        await session.flush()
        await session.refresh(product)

        # подгружаем отношения
        stmt = (
            select(Product)
            .where(Product.id == product.id)
            .options(
                selectinload(Product.category),
                selectinload(Product.enterprise),
            )
        )
        res = await session.execute(stmt)
        return res.scalar_one()

    async def delete_product(self, session: AsyncSession, product_id: int) -> None:
        product = await self.get_product(session, product_id)
        await self.repo.delete(session, product)