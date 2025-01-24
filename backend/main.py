from bson import ObjectId
from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse
#from backend.routes.api_routes import router
from backend.database.connection import mongo_instance
from backend.models.transaction import Transaction, Pair, BodyTransaction, CoinToUser, UserToTransaction
from backend.schema.schemas import list_serial
from datetime import datetime
from bson.objectid import ObjectId

from backend.auth import auth
from backend.routes import admin

import os
from dotenv import load_dotenv, find_dotenv
from backend.LiveData import getBtcUsdtPriceChart, getPairPriceChart, getPrice

# Załaduj plik .env
os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv(find_dotenv())

# Konfiguracja FastAPI
origins = ["http://localhost:20002", "http://127.0.0.1:20002"]
app = FastAPI()

#app.include_router(router, prefix="/api")
# Middleware
app.add_middleware(SessionMiddleware, secret_key="add any string...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["auth"])
app.include_router(admin.router, tags=["admin"])

# Mount statyczne pliki (np. CSS, JS, obrazy)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Załaduj szablony Jinja2
templates = Jinja2Templates(directory="frontend/templates")

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

@app.get("/")
def index(request: Request):
    user = request.session.get("user")
    if check_user(user):
        return templates.TemplateResponse(
            name="index.html", context={"request": request, "user": user}
        )

    return templates.TemplateResponse(name="login.html", context={"request": request})


@app.get("/pairs")
def get_pairs(request: Request):
    user = request.session.get("user")
    if not user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return {
        "btc/usd",
        "eth/usd"
    }

@app.post("/chart")
async def get_chart(request: Request, body: Pair):
    user = request.session.get("user")
    if not user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return getPairPriceChart(body.p_from, body.p_to)

@app.post("/price")
async def get_actual_price(request: Request, body: Pair):
    user = request.session.get("user")
    if not user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        price = getPrice(body.p_from, body.p_to)
        return price
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_all_user_coins(email):
    coins_to_user_collection = mongo_instance.get_coin_to_user_collection()
    coins_collection = mongo_instance.get_coins_collection()
    user_collection = mongo_instance.get_users_collection()
    try:
        user = user_collection.find_one({"email": email})
        if not user:
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



@app.get("/coins")
async def get_all_coins(request: Request):
    user = request.session.get("user")
    if not user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return await get_all_user_coins(user["email"])

async def get_all_user_transaction(email):
    user_to_trans_col = mongo_instance.get_user_to_transaction_collection()
    trans_col = mongo_instance.get_transactions_collection()
    user_collection = mongo_instance.get_users_collection()
    try:
        user = user_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        query = {"user_id": str(user["_id"])}
        print("user id: ", str(user["_id"]))
        projection = {"_id": 0, "user_id": 0}
        transactions = list(user_to_trans_col.find(query, projection))
        print("trans: ", transactions)
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
@app.get("/all_transaction")
async def get_all_transactions(request: Request):
    user = request.session.get("user")
    if not user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return await get_all_user_transaction(user["email"])


@app.post("/transaction")
async def create_transaction(request: Request, body: BodyTransaction):
    user = request.session.get("user")
    if not user:
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

        print("User id: ", user["_id"])
        print("Coin_from: name: ", body.t_from, " id: ", coin_from["_id"])
        print("Coin_from: name: ", body.t_to, " id: ", coin_to["_id"])

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
