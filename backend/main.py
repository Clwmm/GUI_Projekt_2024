from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse
from backend.auth import auth
import os
from dotenv import load_dotenv, find_dotenv

os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv(find_dotenv())

origins = ["http://localhost:20002", "http://127.0.0.1:20002"]
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="add any string...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

app.include_router(auth.router, tags=["auth"])

templates = Jinja2Templates(directory="frontend/templates")


@app.get("/")
def index(request: Request):
    user = request.session.get("user")
    if user:
        return templates.TemplateResponse(
            name="index.html", context={"request": request, "user": user}
        )

    return templates.TemplateResponse(name="login.html", context={"request": request})