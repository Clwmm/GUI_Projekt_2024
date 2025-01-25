from fastapi import APIRouter, HTTPException, status
from backend.database.connection import mongo_instance
from starlette.requests import Request
from fastapi.templating import Jinja2Templates
from backend.models.transaction import Transaction, BodyTransaction, CoinToUser, UserToTransaction, CoinAmount
from bson.objectid import ObjectId
from backend.LiveData import getPrice
from datetime import datetime

templates = Jinja2Templates(directory="frontend/templates")

router = APIRouter()

def check_user(user):
    if not user:
        return False

    user_col = mongo_instance.get_users_collection()
    user = user_col.find_one({"email": user["email"]})
    if user:
        banned = user.get("banned", False)
        if banned:
            return False

    return True

async def get_all_user_coins(email):
    coins_to_user_collection = mongo_instance.get_coin_to_user_collection()
    coins_collection = mongo_instance.get_coins_collection()
    user_collection = mongo_instance.get_users_collection()
    try:
        user = user_collection.find_one({"email": email})
        if not check_user(user):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        query = {"user_id": str(user["_id"])}
        projection = {"_id": 0, "user_id": 0}
        coins = list(coins_to_user_collection.find(query, projection))

        for coin in coins:
            coin_id = coin["coin_id"]
            coin.pop("coin_id", None)
            query = {"_id": ObjectId(coin_id)}
            projection = {"_id": 0}
            name = coins_collection.find_one(query, projection)
            if not name:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            coin["name"] = name["name"]

        return coins
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_all_user_transaction(email):
    user_to_trans_col = mongo_instance.get_user_to_transaction_collection()
    trans_col = mongo_instance.get_transactions_collection()
    user_collection = mongo_instance.get_users_collection()
    try:
        user = user_collection.find_one({"email": email})
        if not check_user(user):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        query = {"user_id": str(user["_id"])}
        projection = {"_id": 0, "user_id": 0}
        transactions = list(user_to_trans_col.find(query, projection))
        result = []

        for trans in transactions:
            trans_id = trans["transaction_id"]
            trans.pop("transaction_id", None)
            query = {"_id": ObjectId(trans_id)}
            projection = {"_id": 0}
            temp = trans_col.find_one(query, projection)
            if not temp:
                return []

            result.append(temp)

        return result
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.post("/deposit")
async def deposit(request: Request, body: CoinAmount):
    user = request.session.get("user")
    if not check_user(user):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    coins_coll = mongo_instance.get_coins_collection()
    coin_to_user_col = mongo_instance.get_coin_to_user_collection()
    user_col = mongo_instance.get_users_collection()

    usd_coin = coins_coll.find_one({"name": "usd"})
    if not usd_coin:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    userdb = user_col.find_one({"email": user["email"]})
    if not userdb:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    value = body.amount

    update_result = coin_to_user_col.update_one(
        {"user_id": str(userdb["_id"]), "coin_id": str(usd_coin["_id"])},
        {"$inc": {"amount": value}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return HTTPException(status_code=status.HTTP_200_OK)

@router.post("/withdraw")
async def withdraw(request: Request, body: CoinAmount):
    user = request.session.get("user")
    if not check_user(user):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


    coins = await get_all_user_coins(user["email"])
    amount = next((item["amount"] for item in coins if item["name"] == "usd"), None)

    value = body.amount

    if value > amount:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    coins_coll = mongo_instance.get_coins_collection()
    coin_to_user_col = mongo_instance.get_coin_to_user_collection()
    user_col = mongo_instance.get_users_collection()

    usd_coin = coins_coll.find_one({"name": "usd"})
    if not usd_coin:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    userdb = user_col.find_one({"email": user["email"]})
    if not userdb:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    update_result = coin_to_user_col.update_one(
        {"user_id": str(userdb["_id"]), "coin_id": str(usd_coin["_id"])},
        {"$inc": {"amount": -value}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return HTTPException(status_code=status.HTTP_200_OK)

@router.get("/coins")
async def get_all_coins(request: Request):
    user = request.session.get("user")
    if not check_user(user):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return await get_all_user_coins(user["email"])

@router.get("/all_transaction")
async def get_all_transactions(request: Request):
    user = request.session.get("user")
    if not check_user(user):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return await get_all_user_transaction(user["email"])


@router.post("/transaction")
async def create_transaction(request: Request, body: BodyTransaction):
    user = request.session.get("user")
    if not check_user(user):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    coins = await get_all_user_coins(user["email"])
    amount = next((item["amount"] for item in coins if item["name"] == body.t_from), None)

    if not amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    if amount < body.amount_from:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        coins_to_user_coll = mongo_instance.get_coin_to_user_collection()
        coins_collection = mongo_instance.get_coins_collection()
        user_collection = mongo_instance.get_users_collection()
        transaction_collection = mongo_instance.get_transactions_collection()
        user_to_trans = mongo_instance.get_user_to_transaction_collection()

        price = getPrice(body.t_from, body.t_to)

        user = user_collection.find_one({"email": user["email"]})

        coin_from = coins_collection.find_one({"name": body.t_from})
        coin_to = coins_collection.find_one({"name": body.t_to})

        query = {"user_id": str(user["_id"]), "coin_id": str(coin_from["_id"])}
        projection = {"$inc": {"amount": -body.amount_from}}
        coins_to_user_coll.update_one(query, projection)

        query = {"user_id": str(user["_id"]), "coin_id": str(coin_to["_id"])}
        temp = coins_to_user_coll.find_one(query)

        amount_to = body.amount_from * price

        if temp:
            projection = {"$inc": {"amount": amount_to}}
            coins_to_user_coll.update_one(query, projection)
        else:
            newCoinToUser = CoinToUser(user_id=ObjectId(user["_id"]), coin_id=ObjectId(coin_to["_id"]), amount=amount_to)
            coins_to_user_coll.insert_one(newCoinToUser.dict())

        newTransaction = Transaction(currency_from=body.t_from, currency_to=body.t_to, amount_from=-body.amount_from, amount_to=amount_to, timestamp=datetime.utcnow())
        inserted_transaction = transaction_collection.insert_one(newTransaction.dict())

        newUserToTransaction = UserToTransaction(user_id=user["_id"], transaction_id=inserted_transaction.inserted_id)
        user_to_trans.insert_one(newUserToTransaction.dict())

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)