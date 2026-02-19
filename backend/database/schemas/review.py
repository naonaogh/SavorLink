"""Схемы для отзывов."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, ConfigDict
from .enterprise import EnterpriseShort
from .product import ProductShort


class EnterpriseReviewCreate(BaseModel):
    """Схема для создания отзыва о предприятии."""
    target_enterprise_id: int
    rating: int
    comment: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Рейтинг должен быть от 1 до 5")
        return v

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 2000:
            raise ValueError("Комментарий не должен превышать 2000 символов")
        return v

    model_config = ConfigDict(from_attributes=True)


class EnterpriseReviewRead(BaseModel):
    """Схема для чтения отзыва о предприятии."""
    id: int
    author_enterprise_id: int
    target_enterprise_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    author_enterprise: Optional[EnterpriseShort] = None
    target_enterprise: Optional[EnterpriseShort] = None

    model_config = ConfigDict(from_attributes=True)


class ProductReviewCreate(BaseModel):
    """Схема для создания отзыва о товаре."""
    product_id: int
    rating: int
    comment: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Рейтинг должен быть от 1 до 5")
        return v

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 2000:
            raise ValueError("Комментарий не должен превышать 2000 символов")
        return v

    model_config = ConfigDict(from_attributes=True)


class ProductReviewRead(BaseModel):
    """Схема для чтения отзыва о товаре."""
    id: int
    author_enterprise_id: int
    product_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    author_enterprise: Optional[EnterpriseShort] = None
    product: Optional[ProductShort] = None

    model_config = ConfigDict(from_attributes=True)
