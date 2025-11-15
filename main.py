from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine
from app.models import Base
from app.routers import auth, dashboard, tickers
from app.routers import news  # NEW
from app.config import settings
from app.tasks.news_tasks import start_news_scheduler  # NEW

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    scheduler = start_news_scheduler()
    yield
    # Shutdown
    scheduler.shutdown()

app = FastAPI(
    title="Stock & Crypto Dashboard API",
    description="Microservice with AI-powered news analysis",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(tickers.router, prefix="/api/tickers", tags=["Tickers"])
app.include_router(news.router, prefix="/api/news", tags=["News & AI"])  # NEW

@app.get("/")
async def root():
    return {
        "message": "Stock & Crypto Dashboard API with AI News",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}



