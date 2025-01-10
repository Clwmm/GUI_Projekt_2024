from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class PydanticObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field=None):
        if not isinstance(v, ObjectId):
            raise TypeError("ObjectId required")
        return str(v)

class User(BaseModel):
    email: EmailStr = Field(..., unique=True)

class UserToTransaction(BaseModel):
    user_id: PydanticObjectId
    transaction_id: PydanticObjectId

class Transaction(BaseModel):
    currency_from: str
    currency_to: str
    amount_from: float
    amount_to: float
    timestamp: datetime

class CoinToUser(BaseModel):
    user_id: PydanticObjectId
    coin_id: PydanticObjectId
    amount: float

class Coin(BaseModel):
    name: str

class Pair(BaseModel):
    p_from: str
    p_to: str

class BodyTransaction(BaseModel):
    t_from: str
    t_to: str
    amount_from: float