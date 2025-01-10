from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter
from dotenv import load_dotenv, find_dotenv
from backend.database.connection import mongo_instance, coins_collection
from backend.models.transaction import User, CoinToUser
import os

load_dotenv(find_dotenv())
# Replace these with your own values from the Google Developer Console
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

oauth = OAuth()
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    client_kwargs={
        "scope": "email openid profile",
        "redirect_url": "http://localhost:8000/auth",
    },
)
router = APIRouter()

templates = Jinja2Templates(directory="frontend/templates")


@router.get("/login")
async def login(request: Request):
    url = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, url)


@router.get("/auth")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        return templates.TemplateResponse(
            name="error.html", context={"request": request, "error": e.error}
        )
    user = token.get("userinfo")
    if user:
        try:
            users_collection = mongo_instance.get_users_collection()
            coins_collection = mongo_instance.get_coins_collection()
            coin_to_user_collection = mongo_instance.get_coin_to_user_collection()
            existing_user = users_collection.find_one({"email": user["email"]})
            if not existing_user:
                new_user = User(email=user["email"])
                inserted_user = users_collection.insert_one(new_user.dict())
                coin = coins_collection.find_one({"name": "usd"})

                newCoinToUser = CoinToUser(user_id=inserted_user.inserted_id, coin_id=coin["_id"], amount=60.0)
                coin_to_user_collection.insert_one(newCoinToUser.dict())

        except OAuthError as e:
            print(e)
        request.session["user"] = dict(user)

    return RedirectResponse("/")


@router.get("/logout")
def logout(request: Request):
    request.session.pop("user")
    request.session.clear()
    return RedirectResponse("/")