"""Схемы для корзины."""
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator, ConfigDict
from .product import ProductShort


class CartItemCreate(BaseModel):
    """Схема для добавления товара в корзину."""
    product_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Количество должно быть не менее 1")
        return v

    model_config = ConfigDict(from_attributes=True)


class CartItemUpdate(BaseModel):
    """Схема для обновления товара в корзине (PATCH)."""
    quantity: int

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Количество должно быть не менее 1")
        return v

    model_config = ConfigDict(from_attributes=True)


class CartItemRead(BaseModel):
    """Схема для чтения товара в корзине."""
    id: int
    product_id: int
    quantity: int
    product: ProductShort

    model_config = ConfigDict(from_attributes=True)


class CartRead(BaseModel):
    """Схема для чтения корзины."""
    id: int
    updated_at: datetime
    items: List[CartItemRead]
    total_amount: Optional[Decimal] = None  # вычисляемое поле

    model_config = ConfigDict(from_attributes=True)
