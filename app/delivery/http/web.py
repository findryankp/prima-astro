from fastapi import APIRouter
from fastapi.responses import HTMLResponse

web_router = APIRouter()

@web_router.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/dashboard/index.html", "r", encoding="utf-8") as f:
        return f.read()

@web_router.get("/insight", response_class=HTMLResponse)
async def read_insight():
    with open("static/insight/insight.html", "r", encoding="utf-8") as f:
        return f.read()

@web_router.get("/forecast", response_class=HTMLResponse)
async def read_forecast():
    with open("static/forecast/forecast.html", "r", encoding="utf-8") as f:
        return f.read()

@web_router.get("/chat", response_class=HTMLResponse)
async def read_chat():
    with open("static/chat/chat.html", "r", encoding="utf-8") as f:
        return f.read()

@web_router.get("/login", response_class=HTMLResponse)
async def read_login():
    with open("static/login/login.html", "r", encoding="utf-8") as f:
        return f.read()

