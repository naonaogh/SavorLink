"""Схемы для предприятий."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from .common import validate_inn, validate_phone


class EnterpriseShort(BaseModel):
    """Короткая версия предприятия для вложенных объектов."""
    id: int
    short_name: str

    model_config = ConfigDict(from_attributes=True)


class EnterpriseCreate(BaseModel):
    """Схема для создания предприятия."""
    short_name: str
    inn: str
    region: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

    @field_validator("short_name")
    @classmethod
    def validate_short_name(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Название не может быть пустым")
        if len(v) > 200:
            raise ValueError("Название не должно превышать 200 символов")
        return v.strip()

    @field_validator("inn")
    @classmethod
    def validate_inn_field(cls, v: str) -> str:
        return validate_inn(v)

    @field_validator("phone")
    @classmethod
    def validate_phone_field(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone(v)

    model_config = ConfigDict(from_attributes=True)


class EnterpriseUpdate(BaseModel):
    """Схема для обновления предприятия (PATCH)."""
    short_name: Optional[str] = None
    inn: Optional[str] = None
    region: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    logo_url: Optional[str] = None  # для будущего использования

    @field_validator("short_name")
    @classmethod
    def validate_short_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError("Название не может быть пустым")
            if len(v) > 200:
                raise ValueError("Название не должно превышать 200 символов")
            return v.strip()
        return v

    @field_validator("inn")
    @classmethod
    def validate_inn_field(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_inn(v)
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone_field(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone(v)

    model_config = ConfigDict(from_attributes=True)


class EnterpriseRead(BaseModel):
    """Схема для чтения предприятия."""
    id: int
    short_name: str
    inn: str
    region: str
    phone: Optional[str] = None
    email: Optional[str] = None
    rating: Optional[float] = None  # вычисляемое поле (avg rating)
    review_count: Optional[int] = None  # вычисляемое поле
    products_count: Optional[int] = None  # вычисляемое поле
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
