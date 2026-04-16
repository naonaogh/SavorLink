from __future__ import annotations
from typing import Sequence
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from backend.database.models import Favorite, Product, Enterprise
from sqlalchemy.orm import selectinload

class FavoriteService:
    async def list_favorite_products(self, session: AsyncSession, user_id: int) -> Sequence[Product]:
        stmt = (
            select(Product)
            .join(Favorite, Favorite.product_id == Product.id)
            .where(Favorite.user_id == user_id)
            .options(
                selectinload(Product.enterprise),
                selectinload(Product.category),
            )
        )
        res = await session.execute(stmt)
        return res.scalars().all()

    async def add_favorite_product(self, session: AsyncSession, user_id: int, product_id: int) -> None:
        # Check if already exists
        stmt = select(Favorite).where(Favorite.user_id == user_id, Favorite.product_id == product_id)
        res = await session.execute(stmt)
        if res.scalars().first():
            return
        
        fav = Favorite(user_id=user_id, product_id=product_id)
        session.add(fav)
        await session.flush()

    async def remove_favorite_product(self, session: AsyncSession, user_id: int, product_id: int) -> None:
        stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.product_id == product_id)
        await session.execute(stmt)
        await session.flush()
