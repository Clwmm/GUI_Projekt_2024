from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse
#from backend.routes.api_routes import router
from backend.database.connection import mongo_instance
from backend.models.transaction import Transaction
from backend.schema.schemas import list_serial

from backend.auth import auth

import os
from dotenv import load_dotenv, find_dotenv
from backend.LiveData import getBtcUsdtPriceChart

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
        data = getBtcUsdtPriceChart()
        candle_data = [
            {"time": '2018-12-22', "open": 75.16, "high": 82.84, "low": 36.16, "close": 45.72},
            {"time": '2018-12-23', "open": 45.12, "high": 53.90, "low": 45.12, "close": 48.09},
            {"time": '2018-12-24', "open": 60.71, "high": 60.71, "low": 53.39, "close": 59.29},
            {"time": '2018-12-25', "open": 68.26, "high": 68.26, "low": 59.04, "close": 60.50},
            {"time": '2018-12-26', "open": 67.71, "high": 105.85, "low": 66.67, "close": 91.04},
            {"time": '2018-12-27', "open": 91.04, "high": 121.40, "low": 82.70, "close": 111.40},
            {"time": '2018-12-28', "open": 111.51, "high": 142.83, "low": 103.34, "close": 131.25},
            {"time": '2018-12-29', "open": 131.33, "high": 151.17, "low": 77.68, "close": 96.43},
            {"time": '2018-12-30', "open": 106.33, "high": 110.20, "low": 90.39, "close": 98.10},
            {"time": '2018-12-31', "open": 109.87, "high": 114.69, "low": 85.66, "close": 111.26},
        ]

        return templates.TemplateResponse(
            name="index.html", context={"request": request, "user": user, "chart_data": data, "candle_data": candle_data}
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


@app.get("/test")
def conn_test(request: Request):
    collection = mongo_instance.collection

    all = list_serial(collection.find())
    return all

@app.post("/test")
async def conn_add_test(item: Transaction):
    collection = mongo_instance.collection
    collection.insert_one(dict(item))