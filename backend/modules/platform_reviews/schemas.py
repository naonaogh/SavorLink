from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict


class PlatformReviewRead(BaseModel):
    id: int
    author_name: str
    author_position: Optional[str] = None
    company_name: Optional[str] = None
    author_role: Literal["BUYER", "SUPPLIER"]
    city: Optional[str] = None
    rating: int
    comment: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlatformReviewList(BaseModel):
    items: List[PlatformReviewRead]
    total: int
    average_rating: Optional[float] = None
