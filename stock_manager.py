import sqlite3
import pandas as pd

DB_NAME = "sparepart.db"

def check_stock(item_query):
    """
    Search for a sparepart by name or item number and return its stock.
    """
    conn = sqlite3.connect(DB_NAME)
    query = f"%{item_query}%"
    
    sql = """
    SELECT item_number, product_name, soh, unit, status
    FROM spareparts 
    WHERE product_name LIKE ? OR item_number LIKE ?
    """
    
    df = pd.read_sql_query(sql, conn, params=(query, query))
    conn.close()
    
    if df.empty:
        return f"Sorry, no sparepart found matching '{item_query}'."
    
    # Format the result
    result = "Here is the stock information:\n"
    for _, row in df.iterrows():
        result += f"- {row['product_name']} ({row['item_number']}): {row['soh']} {row['unit']} (Status: {row['status']})\n"
        
    return result

def get_low_stock_items():
    """
    Return items with WARNING or DANGER status, or stock <= safety stock.
    """
    conn = sqlite3.connect(DB_NAME)
    sql = """
    SELECT item_number, product_name, soh, safety_stock, unit, status
    FROM spareparts 
    WHERE status IN ('WARNING', 'DANGER')
    ORDER BY status DESC
    LIMIT 20
    """
    
    df = pd.read_sql_query(sql, conn)
    conn.close()
    
    if df.empty:
        return "All items have sufficient stock."
        
    result = "Here are the items with low stock warnings:\n"
    for _, row in df.iterrows():
        result += f"- [{row['status']}] {row['product_name']}: {row['soh']} (Safety Stock: {row['safety_stock']})\n"
        
    return result
