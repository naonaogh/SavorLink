"""Схемы для чатов и сообщений."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator, ConfigDict
from .user import UserListItem

class MessageCreate(BaseModel):
    """Схема для создания сообщения."""
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Сообщение не может быть пустым")
        if len(v) > 4000:
            raise ValueError("Сообщение не должно превышать 4000 символов")
        return v.strip()

    model_config = ConfigDict(from_attributes=True)


class MessageRead(BaseModel):
    """Схема для чтения сообщения."""
    id: int
    chat_id: int
    sender_id: int
    content: str
    is_read: bool
    created_at: datetime
    sender: Optional[UserListItem] = None

    model_config = ConfigDict(from_attributes=True)


class ChatCreate(BaseModel):
    """Схема для создания чата."""
    user2_id: int  # user1_id берется из текущего пользователя

    model_config = ConfigDict(from_attributes=True)


class ChatListItem(BaseModel):
    """Схема для списка чатов."""
    id: int
    user1_id: int
    user2_id: int
    created_at: datetime
    user1: Optional[UserListItem] = None
    user2: Optional[UserListItem] = None
    last_message: Optional[MessageRead] = None  # preview последнего сообщения

    model_config = ConfigDict(from_attributes=True)


class ChatRead(BaseModel):
    """Полная схема для чтения чата."""
    id: int
    user1_id: int
    user2_id: int
    created_at: datetime
    user1: Optional[UserListItem] = None
    user2: Optional[UserListItem] = None
    messages: List[MessageRead] = []

    model_config = ConfigDict(from_attributes=True)
