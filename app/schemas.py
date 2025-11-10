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