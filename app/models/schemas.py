from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ArticleBase(BaseModel):
    id: str
    title: str
    slug: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    summary: Optional[str] = None
    category: str
    tags: List[str] = []
    published_at: Optional[str] = None
    is_weekly_event: bool = False


class ArticleResponse(ArticleBase):
    created_at: Optional[str] = None
    notified: bool = False


class PaginatedArticlesResponse(BaseModel):
    total: int
    page: int
    limit: int
    results: List[ArticleResponse]


class WeeklyEventResponse(BaseModel):
    id: int
    article_id: str
    title: str
    url: str
    summary: Optional[str] = None
    bonuses: List[str] = []
    discounts: List[str] = []
    podium_vehicle: Optional[str] = None
    prize_ride: Optional[str] = None
    created_at: Optional[str] = None


class SyncResult(BaseModel):
    new_articles_count: int
    updated_articles_count: int
    message: str
    synced_at: str

