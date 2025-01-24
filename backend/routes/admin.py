from fastapi import APIRouter, HTTPException, status
from backend.database.connection import mongo_instance
from starlette.requests import Request
from fastapi.templating import Jinja2Templates
from backend.models.transaction import TransactionEmail, UserEmail
from bson.objectid import ObjectId

templates = Jinja2Templates(directory="frontend/templates")

router = APIRouter()

def check_admin(user):
    admin_collection = mongo_instance.get_admin_collection()
    admin = admin_collection.find_one({"email": user["email"]})
    if not admin:
        return False
    return True

@router.get("/admin")
def admin_dashboard(request: Request):
    user = request.session.get("user")
    if not user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not check_admin(user):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return templates.TemplateResponse("admin_dashboard.html", context={"request": request, "user": user})

@router.get("/get_all_users")
async def get_all_users(request: Request):
    user = request.session.get("user")
    if not user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not check_admin(user):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user_col = mongo_instance.get_users_collection()
    users = list(user_col.find())
    user_emails = []

    for user in users:
        user_emails.append(user["email"])

    return user_emails

@router.get("/get_users_transactions")
async def get_users_transactions(request: Request):
    user = request.session.get("user")
    if not user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not check_admin(user):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


    trans_col = mongo_instance.get_transactions_collection()
    user_to_transaction_col = mongo_instance.get_user_to_transaction_collection()
    user_col = mongo_instance.get_users_collection()
    transactions = list(trans_col.find())
    transactions_with_emails = []

    for transaction in transactions:
        user_to_transaction = user_to_transaction_col.find_one({"transaction_id": str(transaction["_id"])})
        if user_to_transaction:
            user_id = user_to_transaction["user_id"]
            user_db = user_col.find_one({"_id": ObjectId(user_id)})

            if user_db:
                transaction["user_email"] = user_db.get("email", None)

        transactions_with_emails.append(TransactionEmail(
            currency_from=transaction["currency_from"],
            currency_to=transaction["currency_to"],
            amount_from=transaction["amount_from"],
            amount_to=transaction["amount_to"],
            timestamp=transaction["timestamp"],
            email=transaction.get("user_email", None),
        ))

    return transactions_with_emails


@router.post("/ban_user")
async def ban_user(request: Request, body: UserEmail):
    user = request.session.get("user")
    if not user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not check_admin(user):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user_col = mongo_instance.get_users_collection()
    user = user_col.find_one({"email": body.email})
    if not user:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    update_result = user_col.update_one(
        {"email": body.email},
        {"$set": {"banned": True}},
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return {"message": "success"}


