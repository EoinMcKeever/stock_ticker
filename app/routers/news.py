from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func as sql_func
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, Ticker, NewsArticle, AIInsight
from app.schemas import TickerDashboardData, NewsArticleSchema, AIInsightSchema
from app.auth import get_current_active_user
from app.services.news_service import NewsService

router = APIRouter()

@router.get("/dashboard-news", response_model=List[TickerDashboardData])
async def get_dashboard_with_news(
        hours: int = Query(24, description="Hours of news to fetch"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """Get all user tickers with latest news and AI insights"""
    dashboards = []

    for ticker in current_user.tickers:
        latest_news = db.query(NewsArticle).filter(
            NewsArticle.ticker_id == ticker.id,
            NewsArticle.published_at >= datetime.now() - timedelta(hours=hours)
        ).order_by(desc(NewsArticle.published_at)).limit(10).all()

        latest_insights = db.query(AIInsight).filter(
            AIInsight.ticker_id == ticker.id,
            AIInsight.created_at >= datetime.now() - timedelta(hours=hours)
        ).order_by(desc(AIInsight.created_at)).limit(3).all()

        sources_count = db.query(
            sql_func.count(sql_func.distinct(NewsArticle.news_provider))
        ).filter(
            NewsArticle.ticker_id == ticker.id,
            NewsArticle.published_at >= datetime.now() - timedelta(hours=hours)
        ).scalar() or 0

        # Calculate sentiment
        overall_sentiment = 'neutral'
        if latest_insights:
            sentiments = [i.sentiment for i in latest_insights if i.sentiment]
            if sentiments:
                bullish = sum(1 for s in sentiments if 'bullish' in s.lower())
                bearish = sum(1 for s in sentiments if 'bearish' in s.lower())
                overall_sentiment = 'bullish' if bullish > bearish else ('bearish' if bearish > bullish else 'neutral')

        dashboards.append(TickerDashboardData(
            ticker_symbol=ticker.symbol,
            ticker_name=ticker.name,
            ticker_type=ticker.type,
            latest_news=latest_news,
            ai_insights=latest_insights,
            overall_sentiment=overall_sentiment,
            news_sources_count=sources_count
        ))

    return dashboards


@router.get("/ticker/{ticker_symbol}/news", response_model=List[NewsArticleSchema])
async def get_ticker_news(
        ticker_symbol: str,
        limit: int = Query(20, ge=1, le=100),
        provider: Optional[str] = Query(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """Get news for specific ticker"""
    ticker_symbol = ticker_symbol.upper()

    ticker = db.query(Ticker).filter(Ticker.symbol == ticker_symbol).first()
    if not ticker or ticker not in current_user.tickers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticker not in your list"
        )

    query = db.query(NewsArticle).filter(NewsArticle.ticker_id == ticker.id)

    if provider:
        query = query.filter(NewsArticle.news_provider == provider)

    news = query.order_by(desc(NewsArticle.published_at)).limit(limit).all()
    return news


@router.get("/ticker/{ticker_symbol}/insights", response_model=List[AIInsightSchema])
async def get_ticker_insights(
        ticker_symbol: str,
        limit: int = Query(10, ge=1, le=50),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """Get AI insights for specific ticker"""
    ticker_symbol = ticker_symbol.upper()

    ticker = db.query(Ticker).filter(Ticker.symbol == ticker_symbol).first()
    if not ticker or ticker not in current_user.tickers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticker not in your list"
        )

    insights = db.query(AIInsight).filter(
        AIInsight.ticker_id == ticker.id
    ).order_by(desc(AIInsight.created_at)).limit(limit).all()

    return insights


@router.post("/ticker/{ticker_symbol}/refresh")
async def refresh_ticker_news(
        ticker_symbol: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """Manually refresh news for a ticker"""
    ticker_symbol = ticker_symbol.upper()

    ticker = db.query(Ticker).filter(Ticker.symbol == ticker_symbol).first()
    if not ticker or ticker not in current_user.tickers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticker not in your list"
        )

    news_service = NewsService()
    news_service.save_news_and_insights(ticker.id, ticker.symbol, db)

    return {"message": f"News refreshed for {ticker_symbol}"}