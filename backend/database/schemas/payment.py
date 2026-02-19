"""Схемы для платежей."""
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.database.models import PaymentStatus


class PaymentRead(BaseModel):
    """Схема для чтения платежа."""
    id: int
    order_id: int
    amount: Decimal
    status: PaymentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentConfirm(BaseModel):
    """Схема для подтверждения платежа."""
    pass


class PaymentCancel(BaseModel):
    """Схема для отмены платежа."""
    reason: str = ""

    model_config = ConfigDict(from_attributes=True)
