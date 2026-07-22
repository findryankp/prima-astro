from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.delivery.worker.tasks import process_query_task
from app.usecase import dashboard_usecase, analytics_usecase

app = FastAPI(title="Agentic AI Sparepart Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/api/chat")
def chat_api(req: ChatRequest):
    """
    Endpoint for the Web Chatbot to interact with CrewAI.
    The query is pushed onto the Celery/Redis queue so it's processed
    one-at-a-time alongside requests coming from the Telegram Bot, then we
    block (in FastAPI's threadpool, since this is a sync def) until the
    worker returns the result.
    """
    try:
        async_result = process_query_task.delay(req.message)
        response = async_result.get(timeout=180)
        return {"status": "success", "response": response}
    except Exception as e:
        return {"status": "error", "response": f"An error occurred: {str(e)}"}


@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Returns high level metrics for the dashboard"""
    return dashboard_usecase.get_stats()


@app.get("/api/stock/low")
async def get_low_stock():
    """Returns a list of items with low stock"""
    return dashboard_usecase.get_low_stock_table()


@app.get("/api/transactions/recent")
async def get_recent_transactions():
    """Returns the latest outgoing transactions"""
    return dashboard_usecase.get_recent_transactions()


@app.get("/api/items")
async def get_items():
    """Returns a list of all distinct sparepart items for dropdowns"""
    return dashboard_usecase.get_items_list()


@app.get("/api/forecast/{item_query}")
async def get_forecast(item_query: str):
    """Returns prophet forecast data for charting"""
    return analytics_usecase.get_forecast_data(item_query)


@app.get("/api/insights")
async def get_insights():
    """Returns catalog-wide AI insights: restock alerts, usage trends, and total forecasted demand"""
    return analytics_usecase.get_dashboard_insights()
