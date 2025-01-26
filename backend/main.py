from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from backend.models.transaction import Pair

from backend.auth import auth
from backend.routes import admin
from backend.routes.user import router as user_router
from backend.routes.user import check_user

import os
from dotenv import load_dotenv, find_dotenv
from backend.LiveData import getPairPriceChart, getPrice

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
app.include_router(user_router, tags=["user"])


# Mount statyczne pliki (np. CSS, JS, obrazy)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Załaduj szablony Jinja2
templates = Jinja2Templates(directory="frontend/templates")

@app.get("/")
def index(request: Request):
    user = request.session.get("user")
    if check_user(user):
        return templates.TemplateResponse(
            name="index.html", context={"request": request, "user": user}
        )

    return templates.TemplateResponse(name="login.html", context={"request": request})

@app.get("/profile")
def profile(request: Request):
    return templates.TemplateResponse(name="user_profile.html", context={"request": request})

@app.get("/pairs")
def get_pairs(request: Request):
    user = request.session.get("user")
    if not check_user(user):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return {
        "btc/usd",
        "eth/usd"
    }

@app.post("/chart")
async def get_chart(request: Request, body: Pair):
    user = request.session.get("user")
    if not check_user(user):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return getPairPriceChart(body.p_from, body.p_to)

@app.post("/price")
async def get_actual_price(request: Request, body: Pair):
    user = request.session.get("user")
    if not check_user(user):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        price = getPrice(body.p_from, body.p_to)
        return price
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
