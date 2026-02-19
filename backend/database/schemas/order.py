"""Схемы для заказов."""
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator, ConfigDict
from backend.database.models import OrderStatus, PaymentStatus, DocumentType
from .enterprise import EnterpriseShort
from .product import ProductShort


class OrderItemCreate(BaseModel):
    """Схема для создания позиции заказа."""
    product_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Количество должно быть не менее 1")
        return v

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    """Схема для создания заказа."""
    seller_enterprise_id: int
    items: List[OrderItemCreate]

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: List[OrderItemCreate]) -> List[OrderItemCreate]:
        if not v or len(v) == 0:
            raise ValueError("Заказ должен содержать хотя бы один товар")
        return v

    model_config = ConfigDict(from_attributes=True)


class OrderUpdateStatus(BaseModel):
    """Схема для обновления статуса заказа."""
    status: OrderStatus

    model_config = ConfigDict(from_attributes=True)


class OrderItemRead(BaseModel):
    """Схема для чтения позиции заказа."""
    id: int
    product_id: int
    quantity: int
    price: Decimal
    product: Optional[ProductShort] = None

    model_config = ConfigDict(from_attributes=True)


class PaymentShort(BaseModel):
    """Короткая версия платежа."""
    status: PaymentStatus
    amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class DocumentShort(BaseModel):
    """Короткая версия документа."""
    type: DocumentType
    file_url: str

    model_config = ConfigDict(from_attributes=True)


class OrderListItem(BaseModel):
    """Схема для списка заказов."""
    id: int
    status: OrderStatus
    total_amount: Optional[Decimal] = None
    created_at: datetime
    seller: EnterpriseShort
    buyer: Optional[EnterpriseShort] = None  # для поставщика

    model_config = ConfigDict(from_attributes=True)


class OrderRead(BaseModel):
    """Полная схема для чтения заказа."""
    id: int
    status: OrderStatus
    total_amount: Optional[Decimal] = None
    buyer_enterprise_id: int
    seller_enterprise_id: int
    created_at: datetime
    buyer_enterprise: Optional[EnterpriseShort] = None
    seller_enterprise: EnterpriseShort
    items: List[OrderItemRead]
    payment: Optional[PaymentShort] = None
    documents: List[DocumentShort] = []

    model_config = ConfigDict(from_attributes=True)
