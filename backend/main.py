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