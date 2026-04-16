"""Схемы для заказов."""

from decimal import Decimal
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator, ConfigDict, Field

from backend.database.models import OrderStatus, PaymentStatus, DocumentType
from .enterprise import EnterpriseShort
from .product import ProductShort


class BaseSchema(BaseModel):
    """Базовая схема."""
    model_config = ConfigDict(from_attributes=True)


class OrderItemCreate(BaseSchema):
    """Схема для создания позиции заказа."""
    product_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Количество должно быть не менее 1")
        return v


class OrderCreate(BaseSchema):
    """Схема для создания заказа."""
    seller_enterprise_id: int
    items: List[OrderItemCreate]

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: List[OrderItemCreate]) -> List[OrderItemCreate]:
        if not v:
            raise ValueError("Заказ должен содержать хотя бы один товар")
        return v


class OrderUpdateStatus(BaseSchema):
    """Схема для обновления статуса заказа."""
    status: OrderStatus


class OrderItemRead(BaseSchema):
    """Схема чтения позиции заказа."""
    id: int
    product_id: int
    quantity: int
    price: Decimal
    product: Optional[ProductShort] = None


class PaymentShort(BaseSchema):
    """Короткая информация о платеже."""
    status: PaymentStatus
    amount: Decimal


class DocumentShort(BaseSchema):
    """Короткая информация о документе."""
    type: DocumentType
    file_url: str


class OrderListItem(BaseSchema):
    """Схема элемента списка заказов."""
    id: int
    status: OrderStatus
    total_amount: Optional[Decimal] = None
    created_at: datetime

    seller_enterprise: EnterpriseShort
    buyer_enterprise: Optional[EnterpriseShort] = None
    buyer: Optional[EnterpriseShort] = None

    items: List[OrderItemRead] = Field(default_factory=list)


class OrderRead(BaseSchema):
    """Полная информация о заказе."""
    id: int
    status: OrderStatus
    total_amount: Optional[Decimal] = None

    buyer_enterprise_id: int
    seller_enterprise_id: int

    created_at: datetime

    buyer_enterprise: Optional[EnterpriseShort] = None
    seller_enterprise: EnterpriseShort

    items: List[OrderItemRead] = Field(default_factory=list)
    payment: Optional[PaymentShort] = None
    documents: List[DocumentShort] = Field(default_factory=list)
