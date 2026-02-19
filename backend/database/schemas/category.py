"""Схемы для категорий."""
from pydantic import BaseModel, ConfigDict


class CategoryRead(BaseModel):
    """Схема для чтения категории."""
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
