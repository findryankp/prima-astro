import sqlite3
import pandas as pd
from app.config import DB_NAME


def find_by_query(item_query: str) -> pd.DataFrame:
    """Search spareparts by product name or item number (LIKE match)."""
    conn = sqlite3.connect(DB_NAME)
    query = f"%{item_query}%"
    sql = """
    SELECT item_number, product_name, soh, unit, status
    FROM spareparts
    WHERE product_name LIKE ? OR item_number LIKE ?
    """
    df = pd.read_sql_query(sql, conn, params=(query, query))
    conn.close()
    return df


def get_low_stock(limit: int = 20) -> pd.DataFrame:
    conn = sqlite3.connect(DB_NAME)
    sql = """
    SELECT item_number, product_name, soh, safety_stock, unit, status, moq, last_price
    FROM spareparts
    WHERE status IN ('WARNING', 'DANGER')
    ORDER BY status DESC
    LIMIT ?
    """
    df = pd.read_sql_query(sql, conn, params=(limit,))
    conn.close()
    return df


def get_dashboard_stats() -> dict:
    conn = sqlite3.connect(DB_NAME)
    total_items = pd.read_sql_query("SELECT COUNT(*) as count FROM spareparts", conn)["count"].iloc[0]
    low_stock = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM spareparts WHERE status IN ('WARNING', 'DANGER')", conn
    )["count"].iloc[0]
    conn.close()
    return {"total_items": int(total_items), "low_stock_items": int(low_stock)}


def get_all() -> pd.DataFrame:
    """Full spareparts catalog (item_number, product_name, soh, safety_stock, unit, status)."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        "SELECT item_number, product_name, soh, safety_stock, unit, status FROM spareparts", conn
    )
    conn.close()
    return df


def get_catalog_for_pricing() -> pd.DataFrame:
    """Katalog lengkap plus MOQ & harga terakhir, dipakai buat hitung estimasi biaya restock dan insight harga."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        "SELECT item_number, product_name, unit, soh, safety_stock, moq, last_price, kategori, status FROM spareparts",
        conn,
    )
    conn.close()
    return df


def get_items_with_tx_count() -> pd.DataFrame:
    """All items joined with how many transactions each has (used for the Forecasting item picker)."""
    conn = sqlite3.connect(DB_NAME)
    sql = """
    SELECT
        s.item_number,
        s.product_name,
        COUNT(t.id) as tx_count
    FROM spareparts s
    LEFT JOIN transactions t ON s.item_number = t.item_number
    GROUP BY s.item_number, s.product_name
    ORDER BY s.product_name ASC
    """
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df
