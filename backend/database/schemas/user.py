"""Схемы для пользователей."""
from decimal import Decimal
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from backend.database.models import UserRole
from .enterprise import EnterpriseShort


class UserCreate(BaseModel):
    """Схема для создания пользователя."""
    email: EmailStr
    password: str  # plain password, будет хеширован
    role: UserRole
    enterprise_id: int

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        return v

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Схема для обновления пользователя (PATCH)."""
    email: Optional[EmailStr] = None
    password: Optional[str] = None  # новый пароль
    old_password: Optional[str] = None  # старый пароль для смены
    phone: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        return v

    model_config = ConfigDict(from_attributes=True)


class UserRead(BaseModel):
    """Схема для чтения пользователя."""
    id: int
    email: str
    role: UserRole
    enterprise_id: int
    created_at: datetime
    enterprise: Optional[EnterpriseShort] = None

    model_config = ConfigDict(from_attributes=True)


class UserListItem(BaseModel):
    """Схема для списка пользователей."""
    id: int
    email: str
    role: UserRole
    enterprise_id: int
    enterprise: Optional[EnterpriseShort] = None

    model_config = ConfigDict(from_attributes=True)
