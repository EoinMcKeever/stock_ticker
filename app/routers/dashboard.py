from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User as UserModel, Ticker as TickerModel
from app.schemas import DashboardResponse, TickerBase, User
from app.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
        current_user: UserModel = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Get user's dashboard with all their tickers"""
    # Refresh user to get updated tickers relationship
    db.refresh(current_user)

    return {
        "user": current_user,
        "tickers": current_user.tickers
    }


@router.get("/tickers", response_model=List[TickerBase])
async def get_user_tickers(
        current_user: UserModel = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Get all tickers for the current user"""
    db.refresh(current_user)
    return current_user.tickers