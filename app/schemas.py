from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithTickers(User):
    tickers: List["TickerBase"] = []


# Ticker Schemas
class TickerBase(BaseModel):
    symbol: str
    name: str
    type: str  # 'stock' or 'crypto'

    class Config:
        from_attributes = True


class TickerCreate(BaseModel):
    symbol: str
    name: str
    type: str


class Ticker(TickerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard Schemas
class DashboardResponse(BaseModel):
    user: User
    tickers: List[TickerBase]


class AddTickerRequest(BaseModel):
    symbol: str


class RemoveTickerRequest(BaseModel):
    symbol: str


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class NewsArticleBase(BaseModel):
    title: str
    summary: Optional[str] = None
    url: str
    source: Optional[str] = None
    news_provider: Optional[str] = None
    published_at: datetime
    sentiment_score: Optional[float] = None


class NewsArticleSchema(NewsArticleBase):
    id: int
    ticker_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AIInsightBase(BaseModel):
    insight_type: str
    content: str
    sentiment: Optional[str] = None
    confidence_score: Optional[float] = None
    sources_analyzed: Optional[int] = 0


class AIInsightSchema(AIInsightBase):
    id: int
    ticker_id: int
    news_article_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TickerDashboardData(BaseModel):
    ticker_symbol: str
    ticker_name: str
    ticker_type: str
    latest_news: List[NewsArticleSchema]
    ai_insights: List[AIInsightSchema]
    overall_sentiment: str
    news_sources_count: int

    class Config:
        from_attributes = True