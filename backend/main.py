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
from backend.models.transaction import Transaction, Pair
from backend.schema.schemas import list_serial

from backend.auth import auth

import os
from dotenv import load_dotenv, find_dotenv
from backend.LiveData import getBtcUsdtPriceChart, getPairPriceChart

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

# Mount statyczne pliki (np. CSS, JS, obrazy)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Załaduj szablony Jinja2
templates = Jinja2Templates(directory="frontend/templates")

# Przykładowy endpoint dla strony głównej
@app.get("/")
def index(request: Request):
    user = request.session.get("user")
    if user:
        return templates.TemplateResponse(
            name="index.html", context={"request": request, "user": user}
        )

    return templates.TemplateResponse(name="login.html", context={"request": request})

@app.get("/admin")
def admin_dashboard(request: Request):
    user = request.session.get("user")
    if user:
        return templates.TemplateResponse("admin_dashboard.html", context={"request": request, "user": user})

    return templates.TemplateResponse("admin_dashboard.html", context={"request": request, "user": user})


@app.get("/home")
def admin_dashboard(request: Request):
    user = request.session.get("user")
    if user:
        return templates.TemplateResponse("index.html", context={"request": request, "user": user})

    return templates.TemplateResponse("index.html", context={"request": request, "user": user})


@app.get("/pairs")
def get_pairs(request: Request):
    user = request.session.get("user")
    if not user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return {
        "usd/btc",
        "usd/eth",
        "usd/sol"
    }

@app.post("/chart")
async def get_chart(request: Request, body: Pair):
    user = request.session.get("user")
    if not user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return getPairPriceChart(body.p_from, body.p_to)

async def get_all_user_coins(email):
    coins_to_user_collection = mongo_instance.get_coin_to_user_collection()
    coins_collection = mongo_instance.get_coins_collection()
    user_collection = mongo_instance.get_users_collection()
    try:
        user = user_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        query = {"user_id": str(user["_id"])}
        print("User id: ", user["_id"])
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

@app.get("/test")
def conn_test(request: Request):
    collection = mongo_instance.collection

    all = list_serial(collection.find())
    return all

@app.post("/test")
async def conn_add_test(item: Transaction):
    collection = mongo_instance.collection
    collection.insert_one(dict(item))