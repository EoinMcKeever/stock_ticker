from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.models import Ticker
from app.services.news_service import NewsService
from datetime import datetime


def update_news_for_all_tickers():
    """Background task to update news for all tickers"""
    db = SessionLocal()
    news_service = NewsService()

    try:
        tickers = db.query(Ticker).all()
        print(f"Updating news for {len(tickers)} tickers at {datetime.now()}")

        for ticker in tickers:
            print(f"Processing {ticker.symbol}")
            news_service.save_news_and_insights(ticker.id, ticker.symbol, db)

        print(f"Update completed at {datetime.now()}")
    except Exception as e:
        print(f"Error in news update: {e}")
    finally:
        db.close()


def start_news_scheduler():
    """Start the background scheduler"""
    scheduler = BackgroundScheduler()

    # Update every 4 hours
    scheduler.add_job(
        update_news_for_all_tickers,
        'interval',
        hours=4,
        id='news_update_job'
    )

    # Run on startup
    scheduler.add_job(
        update_news_for_all_tickers,
        'date',
        run_date=datetime.now()
    )

    scheduler.start()
    print("News scheduler started")
    return scheduler