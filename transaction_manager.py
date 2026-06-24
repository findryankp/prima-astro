import sqlite3
import pandas as pd

DB_NAME = "sparepart.db"

def view_outgoing_stock(department=None, limit=10):
    """
    View recent outgoing stock transactions. Can be filtered by department.
    """
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
    
    if df.empty:
        dept_str = f" for department '{department}'" if department else ""
        return f"No outgoing stock found{dept_str}."
        
    result = f"Recent outgoing stock transactions:\n"
    for _, row in df.iterrows():
        # Clean timestamp to date only if needed
        date_str = str(row['tanggal']).split(" ")[0]
        result += f"- {date_str}: {row['qty_out']}x {row['product_name']} (Dept: {row['department']}, PIC: {row['pic']})\n"
        
    return result

def get_top_users_of_item(item_query):
    """
    Find which departments or PICs use a specific item the most.
    """
    conn = sqlite3.connect(DB_NAME)
    query = f"%{item_query}%"
    
    sql = """
    SELECT department, pic, SUM(qty_out) as total_qty
    FROM transactions
    WHERE product_name LIKE ? OR item_number LIKE ?
    GROUP BY department, pic
    ORDER BY total_qty DESC
    LIMIT 5
    """
    
    df = pd.read_sql_query(sql, conn, params=(query, query))
    conn.close()
    
    if df.empty:
        return f"No transactions found for '{item_query}'."
        
    result = f"Top users for '{item_query}':\n"
    for _, row in df.iterrows():
        result += f"- {row['department']} (PIC: {row['pic']}): {row['total_qty']} units\n"
        
    return result
