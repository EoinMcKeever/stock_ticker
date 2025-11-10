from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User as UserModel, Ticker as TickerModel
from app.schemas import AddTickerRequest, RemoveTickerRequest, Ticker, TickerCreate
from app.auth import get_current_active_user

router = APIRouter()


@router.post("/add", response_model=Ticker)
async def add_ticker_to_dashboard(
        request: AddTickerRequest,
        current_user: UserModel = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Add a ticker to user's dashboard.
    Note: You should call your search/validation logic before calling this endpoint.
    This endpoint assumes the ticker symbol is valid.
    """
    symbol = request.symbol.upper()

    # Check if ticker exists in database
    ticker = db.query(TickerModel).filter(TickerModel.symbol == symbol).first()

    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker {symbol} not found. Please validate ticker first."
        )

    # Check if user already has this ticker
    if ticker in current_user.tickers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticker {symbol} is already in your dashboard"
        )

    # Add ticker to user's dashboard
    current_user.tickers.append(ticker)
    db.commit()
    db.refresh(current_user)

    return ticker


@router.post("/create", response_model=Ticker, status_code=status.HTTP_201_CREATED)
async def create_ticker(
        ticker_data: TickerCreate,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_active_user)
):
    """
    Create a new ticker in the system.
    This should be called after validating the ticker through your search logic.
    """
    symbol = ticker_data.symbol.upper()

    # Check if ticker already exists
    existing_ticker = db.query(TickerModel).filter(TickerModel.symbol == symbol).first()
    if existing_ticker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticker {symbol} already exists"
        )

    # Validate type
    if ticker_data.type not in ['stock', 'crypto']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type must be either 'stock' or 'crypto'"
        )

    # Create new ticker
    new_ticker = TickerModel(
        symbol=symbol,
        name=ticker_data.name,
        type=ticker_data.type
    )

    db.add(new_ticker)
    db.commit()
    db.refresh(new_ticker)

    return new_ticker


@router.delete("/remove/{symbol}")
async def remove_ticker_from_dashboard(
        symbol: str,
        current_user: UserModel = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Remove a ticker from user's dashboard"""
    symbol = symbol.upper()

    # Find the ticker
    ticker = db.query(TickerModel).filter(TickerModel.symbol == symbol).first()

    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker {symbol} not found"
        )

    # Check if user has this ticker
    if ticker not in current_user.tickers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticker {symbol} is not in your dashboard"
        )

    # Remove ticker from user's dashboard
    current_user.tickers.remove(ticker)
    db.commit()

    return {
        "message": f"Ticker {symbol} removed successfully",
        "symbol": symbol
    }


@router.get("/all", response_model=List[Ticker])
async def get_all_tickers(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100
):
    """Get all available tickers in the system"""
    tickers = db.query(TickerModel).offset(skip).limit(limit).all()
    return tickers


@router.get("/search/{symbol}", response_model=Ticker)
async def get_ticker_by_symbol(
        symbol: str,
        db: Session = Depends(get_db)
):
    """Get ticker information by symbol"""
    ticker = db.query(TickerModel).filter(TickerModel.symbol == symbol.upper()).first()

    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker {symbol} not found"
        )

    return ticker