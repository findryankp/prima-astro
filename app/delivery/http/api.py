import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.config import REPORTS_DIR
from app.delivery.worker.celery_app import celery_app
from app.delivery.worker.tasks import process_query_task, generate_report_task
from app.usecase import dashboard_usecase, analytics_usecase, purchasing_usecase, pricing_usecase

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


@app.get("/api/purchase-orders/draft")
async def get_draft_purchase_orders():
    """Returns a draft PO recommendation (order qty + estimated cost) for items needing restock"""
    return purchasing_usecase.draft_purchase_orders()


@app.get("/api/pricing/insights")
async def get_pricing_insights():
    """Returns catalog-wide pricing insight: most expensive items and highest stock value items"""
    return pricing_usecase.get_price_insights()


@app.post("/api/reports/generate")
def generate_report():
    """Queues a background job (Celery) that builds a CSV insight report. Returns a task_id to poll."""
    async_result = generate_report_task.delay()
    return {"status": "queued", "task_id": async_result.id}


@app.get("/api/reports/status/{task_id}")
def get_report_status(task_id: str):
    """Poll this with the task_id from /api/reports/generate to know when the CSV is ready."""
    async_result = celery_app.AsyncResult(task_id)
    if not async_result.ready():
        return {"status": "pending"}

    result = async_result.result
    if isinstance(result, dict) and result.get("status") == "success":
        return {"status": "done", "filename": result["filename"]}
    message = result.get("message") if isinstance(result, dict) else str(result)
    return {"status": "failed", "message": message}


@app.get("/api/reports/download/{filename}")
def download_report(filename: str):
    """Downloads a previously generated CSV report by filename."""
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    filepath = os.path.join(REPORTS_DIR, filename)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(filepath, media_type="text/csv", filename=filename)
