from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    email: EmailStr = Field(..., unique=True)

class UserToTransaction(BaseModel):
    user_id: int
    transaction_id: int

class Transaction(BaseModel):
    transaction_id: int = Field(..., unique=True)
    currency_from: str
    currency_to: str
    amount_from: float
    amount_to: float
    timestamp: datetime

class CoinToUser(BaseModel):
    user_id: int
    coin_id: int
    amount: float

class Coin(BaseModel):
    coin_id: int = Field(..., unique=True)
    name: str