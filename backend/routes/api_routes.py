'''

from fastapi import APIRouter, HTTPException, Depends
from models.transaction import Transaction
from database.connection import get_db
from typing import List

router = APIRouter()

@router.post("/transactions")
async def create_transaction(transaction: Transaction, db=Depends(get_db)):
    async with db.acquire() as connection:
        try:
            await connection.execute(
                """
                INSERT INTO transactions (user_id, currency, amount, transaction_type, timestamp)
                VALUES ($1, $2, $3, $4, NOW())
                """,
                transaction.user_id,
                transaction.currency,
                transaction.amount,
                transaction.transaction_type,
            )
            return {"message": "Transaction added successfully."}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


from models.transaction import Transaction

@router.get("/transactions/{user_id}", response_model=List[Transaction])
async def get_transactions(user_id: int, db=Depends(get_db)):
    async with db.acquire() as connection:
        try:
            rows = await connection.fetch(
                """
                SELECT user_id, currency, amount, transaction_type, timestamp
                FROM transactions
                WHERE user_id = $1
                ORDER BY timestamp DESC
                """,
                user_id,
            )
            return [Transaction(**row) for row in rows]
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
 '''