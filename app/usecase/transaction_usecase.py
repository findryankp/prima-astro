from app.repository import transaction_repository


def view_outgoing_stock(department: str = None) -> str:
    """Return a human-readable list of recent outgoing stock transactions."""
    if department and department.lower() == "none":
        department = None

    df = transaction_repository.get_outgoing(department=department, limit=10)

    if df.empty:
        dept_str = f" for department '{department}'" if department else ""
        return f"No outgoing stock found{dept_str}."

    result = "Recent outgoing stock transactions:\n"
    for _, row in df.iterrows():
        date_str = str(row["tanggal"]).split(" ")[0]
        result += f"- {date_str}: {row['qty_out']}x {row['product_name']} (Dept: {row['department']}, PIC: {row['pic']})\n"
    return result


def get_top_users_of_item(item_query: str) -> str:
    """Return a human-readable list of the departments/PICs that use an item the most."""
    df = transaction_repository.get_top_users(item_query, limit=5)

    if df.empty:
        return f"No transactions found for '{item_query}'."

    result = f"Top users for '{item_query}':\n"
    for _, row in df.iterrows():
        result += f"- {row['department']} (PIC: {row['pic']}): {row['total_qty']} units\n"
    return result
