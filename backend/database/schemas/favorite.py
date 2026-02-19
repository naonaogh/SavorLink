"""Схемы для избранного."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from .product import ProductShort


class FavoriteCreate(BaseModel):
    """Схема для добавления в избранное."""
    product_id: int

    model_config = ConfigDict(from_attributes=True)


class FavoriteRead(BaseModel):
    """Схема для чтения избранного."""
    id: int
    product_id: int
    created_at: datetime
    product: Optional[ProductShort] = None

    model_config = ConfigDict(from_attributes=True)
