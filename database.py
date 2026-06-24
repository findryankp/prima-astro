import sqlite3
import json
import os

def init_db(db_name="sparepart.db"):
    # Connect to SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create spareparts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS spareparts (
        no INTEGER,
        item_number TEXT PRIMARY KEY,
        product_name TEXT,
        unit TEXT,
        soh REAL,
        safety_stock REAL,
        kategori TEXT,
        moq REAL,
        total_kebutuhan_bulan REAL,
        order_qty REAL,
        last_price REAL,
        status TEXT
    )
    """)

    # Create transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        item_number TEXT,
        product_name TEXT,
        pic TEXT,
        department TEXT,
        tanggal TEXT,
        qty REAL,
        status TEXT,
        keterangan TEXT,
        qty_out REAL,
        created_at TEXT,
        updated_at TEXT,
        nomor_pesanan TEXT,
        sync_wms TEXT,
        FOREIGN KEY (item_number) REFERENCES spareparts(item_number)
    )
    """)
    conn.commit()
    return conn

def safe_float(val):
    try:
        if val == "" or val == "-" or val is None:
            return 0.0
        return float(val)
    except ValueError:
        return 0.0

def load_spareparts(conn, json_file="sparepart-table-data.json"):
    if not os.path.exists(json_file):
        print(f"File {json_file} not found.")
        return

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    cursor = conn.cursor()
    count = 0
    for item in data:
        cursor.execute("""
        INSERT OR REPLACE INTO spareparts (
            no, item_number, product_name, unit, soh, safety_stock, kategori, moq, 
            total_kebutuhan_bulan, order_qty, last_price, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.get("No"),
            item.get("Item Number"),
            item.get("Product Name"),
            item.get("Unit"),
            safe_float(item.get("SOH")),
            safe_float(item.get("Safety Stock")),
            item.get("Kategori"),
            safe_float(item.get("MOQ")),
            safe_float(item.get("Total Kebutuhan Bulan")),
            safe_float(item.get("Order")),
            safe_float(item.get("Last Price")),
            item.get("Status")
        ))
        count += 1

    conn.commit()
    print(f"Loaded {count} spareparts.")

def load_transactions(conn, json_file="transaction.json"):
    if not os.path.exists(json_file):
        print(f"File {json_file} not found.")
        return

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = data.get("rows", [])
    cursor = conn.cursor()
    count = 0
    for row in rows:
        cursor.execute("""
        INSERT OR REPLACE INTO transactions (
            id, item_number, product_name, pic, department, tanggal, qty, status, 
            keterangan, qty_out, created_at, updated_at, nomor_pesanan, sync_wms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get("id"),
            row.get("item_number"),
            row.get("product_name"),
            row.get("pic"),
            row.get("department"),
            row.get("tanggal"),
            safe_float(row.get("qty")),
            row.get("status"),
            row.get("keterangan"),
            safe_float(row.get("qty_out")),
            row.get("created_at"),
            row.get("updated_at"),
            row.get("nomor_pesanan"),
            row.get("sync_wms")
        ))
        count += 1

    conn.commit()
    print(f"Loaded {count} transactions.")

if __name__ == "__main__":
    db_conn = init_db()
    print("Database initialized.")
    load_spareparts(db_conn)
    load_transactions(db_conn)
    db_conn.close()
    print("Data migration complete.")
