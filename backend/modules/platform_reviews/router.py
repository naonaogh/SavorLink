from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import PlatformReview
from backend.database.session import get_session
from backend.modules.platform_reviews.schemas import PlatformReviewList


router = APIRouter(prefix="/platform-reviews", tags=["platform-reviews"])


@router.get("", response_model=PlatformReviewList)
async def list_platform_reviews(session: AsyncSession = Depends(get_session)):
    stmt = select(PlatformReview).order_by(PlatformReview.created_at.desc(), PlatformReview.id.desc())
    reviews = (await session.execute(stmt)).scalars().all()

    total = len(reviews)
    average = round(sum(r.rating for r in reviews) / total, 1) if total else None
    return PlatformReviewList(items=list(reviews), total=total, average_rating=average)
