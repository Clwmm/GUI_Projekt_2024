from pydantic import BaseModel
from typing import Optional

class Transaction(BaseModel):
    user_id: int
    currency: str
    amount: float
    transaction_type: str #tutaj buy albo sell
    timestamp: Optional[str] = None # nwm czy to potrzebne bedzie
