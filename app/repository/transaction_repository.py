import sqlite3
import pandas as pd
from app.config import DB_NAME


def get_outgoing(department: str = None, limit: int = 10) -> pd.DataFrame:
    conn = sqlite3.connect(DB_NAME)
    if department:
        sql = """
        SELECT tanggal, product_name, qty_out, department, pic
        FROM transactions
        WHERE department LIKE ?
        ORDER BY tanggal DESC
        LIMIT ?
        """
        df = pd.read_sql_query(sql, conn, params=(f"%{department}%", limit))
    else:
        sql = """
        SELECT tanggal, product_name, qty_out, department, pic
        FROM transactions
        ORDER BY tanggal DESC
        LIMIT ?
        """
        df = pd.read_sql_query(sql, conn, params=(limit,))
    conn.close()
    return df


def get_top_users(item_query: str, limit: int = 5) -> pd.DataFrame:
    conn = sqlite3.connect(DB_NAME)
    query = f"%{item_query}%"
    sql = """
    SELECT department, pic, SUM(qty_out) as total_qty
    FROM transactions
    WHERE product_name LIKE ? OR item_number LIKE ?
    GROUP BY department, pic
    ORDER BY total_qty DESC
    LIMIT ?
    """
    df = pd.read_sql_query(sql, conn, params=(query, query, limit))
    conn.close()
    return df


def get_for_item(item_query: str) -> pd.DataFrame:
    """All outgoing transactions for a given item (used for trend analysis & forecasting)."""
    conn = sqlite3.connect(DB_NAME)
    query = f"%{item_query}%"
    sql = """
    SELECT tanggal, qty_out, product_name
    FROM transactions
    WHERE product_name LIKE ? OR item_number LIKE ?
    """
    df = pd.read_sql_query(sql, conn, params=(query, query))
    conn.close()
    return df


def get_all() -> pd.DataFrame:
    """Full transaction history (used for catalog-wide dashboard insights)."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT item_number, product_name, tanggal, qty_out FROM transactions", conn)
    conn.close()
    return df


def count_all() -> int:
    conn = sqlite3.connect(DB_NAME)
    count = pd.read_sql_query("SELECT COUNT(*) as count FROM transactions", conn)["count"].iloc[0]
    conn.close()
    return int(count)
