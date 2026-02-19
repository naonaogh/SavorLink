from __future__ import annotations

from decimal import Decimal
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

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
        # В MVP enterprise_id берём из авторизованного пользователя/контекста (пока параметром).
        product = Product(
            name=data.name,
            description=data.description,
            price=data.price,
            min_order_qty=data.min_order_qty,
            quantity_in_stock=data.quantity_in_stock,
            enterprise_id=enterprise_id,
            category_id=data.category_id,
        )
        return await self.repo.create(session, product)

    async def update_product(self, session: AsyncSession, product_id: int, data: ProductUpdate) -> Product:
        product = await self.get_product(session, product_id)

        if data.name is not None:
            product.name = data.name
        if data.description is not None:
            product.description = data.description
        if data.price is not None:
            product.price = data.price
        if data.min_order_qty is not None:
            product.min_order_qty = data.min_order_qty
        if data.quantity_in_stock is not None:
            product.quantity_in_stock = data.quantity_in_stock
        if data.category_id is not None:
            product.category_id = data.category_id

        await session.flush()
        await session.refresh(product)
        return product

    async def delete_product(self, session: AsyncSession, product_id: int) -> None:
        product = await self.get_product(session, product_id)
        await self.repo.delete(session, product)
