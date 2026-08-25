from app.repository import sparepart_repository


def get_price_insights(top_n: int = 8) -> dict:
    """Ringkasan sisi harga: item termahal per unit, dan item yang paling besar nilai stoknya (soh x harga)."""
    catalog = sparepart_repository.get_catalog_for_pricing()
    if catalog.empty:
        return {"status": "error", "message": "Data katalog kosong, belum bisa dianalisa."}

    catalog = catalog.fillna({"last_price": 0, "moq": 0, "soh": 0})
    catalog = catalog[catalog["last_price"] > 0]
    if catalog.empty:
        return {"status": "error", "message": "Belum ada data harga (last_price) yang terisi di katalog."}

    catalog["stock_value"] = catalog["soh"] * catalog["last_price"]

    most_expensive = catalog.sort_values("last_price", ascending=False).head(top_n)
    highest_value = catalog.sort_values("stock_value", ascending=False).head(top_n)

    cols = ["item_number", "product_name", "unit", "soh", "last_price", "stock_value"]
    return {
        "status": "success",
        "total_stock_value": round(float(catalog["stock_value"].sum()), 2),
        "item_count_with_price": int(len(catalog)),
        "most_expensive_items": most_expensive[cols].to_dict(orient="records"),
        "highest_stock_value_items": highest_value[cols].to_dict(orient="records"),
    }


def estimate_item_price(item_query: str) -> dict:
    """Cari harga terakhir + nilai stok yang lagi disimpan buat satu item spesifik."""
    catalog = sparepart_repository.get_catalog_for_pricing()
    match = catalog[
        catalog["product_name"].str.contains(item_query, case=False, na=False)
        | catalog["item_number"].str.contains(item_query, case=False, na=False)
    ]

    if match.empty:
        return {"status": "error", "message": f"Item '{item_query}' tidak ditemukan di katalog."}

    row = match.iloc[0]
    last_price = float(row["last_price"] or 0)
    soh = float(row["soh"] or 0)
    return {
        "status": "success",
        "item_number": row["item_number"],
        "product_name": row["product_name"],
        "unit": row["unit"],
        "last_price": last_price,
        "soh": soh,
        "stock_value": round(soh * last_price, 2),
    }
