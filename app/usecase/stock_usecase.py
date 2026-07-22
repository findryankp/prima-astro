from app.repository import sparepart_repository


def check_stock(item_query: str) -> str:
    """Return a human-readable stock report for items matching the query."""
    df = sparepart_repository.find_by_query(item_query)

    if df.empty:
        return f"Sorry, no sparepart found matching '{item_query}'."

    result = "Here is the stock information:\n"
    for _, row in df.iterrows():
        result += f"- {row['product_name']} ({row['item_number']}): {row['soh']} {row['unit']} (Status: {row['status']})\n"
    return result


def get_low_stock_items() -> str:
    """Return a human-readable list of items in WARNING or DANGER status."""
    df = sparepart_repository.get_low_stock(limit=20)

    if df.empty:
        return "All items have sufficient stock."

    result = "Here are the items with low stock warnings:\n"
    for _, row in df.iterrows():
        result += f"- [{row['status']}] {row['product_name']}: {row['soh']} (Safety Stock: {row['safety_stock']})\n"
    return result
