from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import pandas as pd
from agent import process_user_query
from analytics import get_forecast_data

app = FastAPI(title="Agentic AI Sparepart Dashboard API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

DB_NAME = "sparepart.db"

class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/chat")
async def chat_api(req: ChatRequest):
    """Endpoint for the Web Chatbot to interact with CrewAI"""
    try:
        response = await process_user_query(req.message)
        return {"status": "success", "response": response}
    except Exception as e:
        return {"status": "error", "response": f"An error occurred: {str(e)}"}

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Returns high level metrics for the dashboard"""
    conn = sqlite3.connect(DB_NAME)
    
    # Total distinct items
    total_items = pd.read_sql_query("SELECT COUNT(*) as count FROM spareparts", conn)['count'].iloc[0]
    
    # Items in WARNING or DANGER
    low_stock = pd.read_sql_query("SELECT COUNT(*) as count FROM spareparts WHERE status IN ('WARNING', 'DANGER')", conn)['count'].iloc[0]
    
    # Total transactions
    total_tx = pd.read_sql_query("SELECT COUNT(*) as count FROM transactions", conn)['count'].iloc[0]
    
    conn.close()
    return {
        "total_items": int(total_items),
        "low_stock_items": int(low_stock),
        "total_transactions": int(total_tx)
    }

@app.get("/api/stock/low")
async def get_low_stock():
    """Returns a list of items with low stock"""
    conn = sqlite3.connect(DB_NAME)
    sql = """
    SELECT item_number, product_name, soh, safety_stock, unit, status
    FROM spareparts 
    WHERE status IN ('WARNING', 'DANGER')
    ORDER BY status DESC
    LIMIT 10
    """
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df.to_dict(orient="records")

@app.get("/api/transactions/recent")
async def get_recent_transactions():
    """Returns the latest outgoing transactions"""
    conn = sqlite3.connect(DB_NAME)
    sql = """
    SELECT tanggal, product_name, qty_out, department, pic
    FROM transactions
    ORDER BY tanggal DESC
    LIMIT 10
    """
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df.to_dict(orient="records")

@app.get("/api/items")
async def get_items():
    """Returns a list of all distinct sparepart items for dropdowns"""
    conn = sqlite3.connect(DB_NAME)
    sql = "SELECT item_number, product_name FROM spareparts ORDER BY product_name ASC"
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df.to_dict(orient="records")

@app.get("/api/forecast/{item_query}")
async def get_forecast(item_query: str):
    """Returns prophet forecast data for charting"""
    return get_forecast_data(item_query)
