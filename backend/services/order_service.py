from __future__ import annotations

from decimal import Decimal
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import Order, OrderItem, OrderStatus
from backend.database.schemas.order import OrderCreate, OrderUpdateStatus
from backend.database.repository.order_repository import OrderRepository
from backend.database.repository.product_repository import ProductRepository


class OrderService:
    def __init__(self, repo: OrderRepository | None = None, product_repo: ProductRepository | None = None) -> None:
        self.repo = repo or OrderRepository()
        self.product_repo = product_repo or ProductRepository()

    async def list_orders(self, session: AsyncSession, *, limit: int = 50, offset: int = 0) -> Sequence[Order]:
        return await self.repo.list(session, limit=limit, offset=offset)

    async def get_order(self, session: AsyncSession, order_id: int) -> Order:
        order = await self.repo.get(session, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")
        return order

    async def create_order(self, session: AsyncSession, data: OrderCreate, *, buyer_enterprise_id: int) -> Order:
        order = Order(
            status=OrderStatus.CREATED,
            buyer_enterprise_id=buyer_enterprise_id,
            seller_enterprise_id=data.seller_enterprise_id,
        )
        total = Decimal("0")

        # Позиции: цену фиксируем на момент заказа
        for item in data.items:
            product = await self.product_repo.get(session, item.product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"Товар не найден: {item.product_id}")
            price = Decimal(str(product.price))
            total += price * Decimal(item.quantity)
            order.items.append(
                OrderItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=price,
                )
            )

        order.total_amount = total
        return await self.repo.create(session, order)

    async def update_status(self, session: AsyncSession, order_id: int, data: OrderUpdateStatus) -> Order:
        order = await self.get_order(session, order_id)
        # MVP: без проверки ролей/правил переходов (позже добавим)
        order.status = data.status
        await session.flush()
        await session.refresh(order)
        return order

