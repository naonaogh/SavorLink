"""Общие схемы и валидаторы для всех схем."""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from datetime import datetime


class BaseSchema(BaseModel):
    """Базовая схема с настройками."""
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }
    )


def validate_inn(value: str) -> str:
    """Валидация ИНН (10 или 12 цифр)."""
    if not value.isdigit():
        raise ValueError("ИНН должен содержать только цифры")
    if len(value) not in (10, 12):
        raise ValueError("ИНН должен содержать 10 или 12 цифр")
    return value


def validate_phone(value: Optional[str]) -> Optional[str]:
    """Валидация телефона."""
    if value is None:
        return None
    # Убираем все пробелы и дефисы
    cleaned = value.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    # Проверяем формат: +7XXXXXXXXXX или 8XXXXXXXXXX или 7XXXXXXXXXX
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]
    if cleaned.startswith("8"):
        cleaned = "7" + cleaned[1:]
    if not cleaned.isdigit() or len(cleaned) < 10 or len(cleaned) > 15:
        raise ValueError("Неверный формат телефона")
    return value
