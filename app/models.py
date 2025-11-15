from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Table, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Association table for many-to-many relationship between users and tickers
user_tickers = Table(
    'user_tickers',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('ticker_id', Integer, ForeignKey('tickers.id', ondelete='CASCADE'), primary_key=True),
    Column('added_at', DateTime(timezone=True), server_default=func.now())
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tickers = relationship("Ticker", secondary=user_tickers, back_populates="users")


class Ticker(Base):
    __tablename__ = "tickers"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'stock' or 'crypto'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    users = relationship("User", secondary=user_tickers, back_populates="tickers")

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    ticker_id = Column(Integer, ForeignKey('tickers.id', ondelete='CASCADE'), nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text)
    url = Column(String, nullable=False, unique=True)
    source = Column(String)
    news_provider = Column(String)  # 'yfinance', 'alphavantage', 'finnhub', 'marketaux'
    published_at = Column(DateTime(timezone=True), nullable=False)
    sentiment_score = Column(Float)  # -1 to 1 (negative to positive)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ticker = relationship("Ticker", backref="news_articles")
    ai_insights = relationship("AIInsight", back_populates="news_article", cascade="all, delete-orphan")


class AIInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, index=True)
    ticker_id = Column(Integer, ForeignKey('tickers.id', ondelete='CASCADE'), nullable=False)
    news_article_id = Column(Integer, ForeignKey('news_articles.id', ondelete='CASCADE'), nullable=True)
    insight_type = Column(String, nullable=False)  # 'news_summary', 'market_analysis', 'trend_analysis'
    content = Column(Text, nullable=False)
    sentiment = Column(String)  # 'bullish', 'bearish', 'neutral'
    confidence_score = Column(Float)  # 0 to 1
    sources_analyzed = Column(Integer, default=0)  # Number of sources used
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ticker = relationship("Ticker", backref="ai_insights")
    news_article = relationship("NewsArticle", back_populates="ai_insights")