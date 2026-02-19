"""Схемы для документов."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.database.models import DocumentType


class DocumentRead(BaseModel):
    """Схема для чтения документа."""
    id: int
    order_id: int
    type: DocumentType
    file_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
