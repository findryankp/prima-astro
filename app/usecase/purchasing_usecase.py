import math
from app.repository import sparepart_repository
from app.usecase import analytics_usecase

# Kalau item lagi gak ketahuan pola pemakaiannya, kita tetap kasih buffer 14 hari
# ke depan biar draft PO gak nol qty gara-gara avg_daily_usage kebetulan 0.
FALLBACK_LEAD_TIME_DAYS = 14


def _order_qty_for(row) -> float:
    moq = float(row.get("moq") or 0)
    safety_stock = float(row.get("safety_stock") or 0)
    soh = float(row.get("soh") or 0)
    avg_daily = float(row.get("avg_daily_usage") or 0)

    gap_to_safety = max(0.0, safety_stock - soh)
    buffer_need = avg_daily * FALLBACK_LEAD_TIME_DAYS
    needed = max(gap_to_safety, buffer_need)

    qty = max(moq, needed)
    return math.ceil(qty) if qty > 0 else 0.0


def draft_purchase_orders(limit: int = 10) -> dict:
    """
    Bikin draft rekomendasi Purchase Order dari item-item yang lagi butuh
    restock (hasil dari analytics_usecase.get_dashboard_insights). Qty order
    dihitung minimal sebesar MOQ, dan disesuaikan naik kalau selisih ke
    safety stock atau kebutuhan 14 hari ke depan lebih besar dari MOQ-nya.
    """
    insight = analytics_usecase.get_dashboard_insights()
    if insight.get("status") != "success":
        return {"status": "error", "message": insight.get("message", "Data insight kosong.")}

    alerts = insight.get("restock_alerts", [])
    if not alerts:
        return {"status": "empty", "message": "Belum ada item yang butuh restock mendesak."}

    catalog = sparepart_repository.get_catalog_for_pricing().set_index("item_number")

    items = []
    total_cost = 0.0
    for alert in alerts[:limit]:
        item_no = alert["item_number"]
        if item_no not in catalog.index:
            continue
        cat_row = catalog.loc[item_no]

        merged = {**cat_row.to_dict(), **alert}
        order_qty = _order_qty_for(merged)
        if order_qty <= 0:
            continue

        last_price = float(cat_row.get("last_price") or 0)
        estimated_cost = round(order_qty * last_price, 2)
        total_cost += estimated_cost

        items.append({
            "item_number": item_no,
            "product_name": alert["product_name"],
            "unit": alert["unit"],
            "soh": alert["soh"],
            "moq": float(cat_row.get("moq") or 0),
            "order_qty": order_qty,
            "last_price": last_price,
            "estimated_cost": estimated_cost,
            "days_to_stockout": alert.get("days_to_stockout"),
        })

    if not items:
        return {"status": "empty", "message": "Item butuh restock ada, tapi datanya belum lengkap (moq/harga kosong)."}

    return {
        "status": "success",
        "as_of_date": insight["as_of_date"],
        "total_estimated_cost": round(total_cost, 2),
        "items": items,
    }
