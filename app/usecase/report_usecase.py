import csv
import os
from app.config import REPORTS_DIR
from app.usecase import analytics_usecase, purchasing_usecase


def generate_insight_report() -> dict:
    """
    Bikin file CSV berisi restock alert, tren naik/turun, dan draft PO —
    dijalankan lewat Celery task karena bisa nyentuh Prophet/analisa berat,
    jadi request-nya gak nunggu di depan (endpoint langsung balikin task_id).
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)

    insight = analytics_usecase.get_dashboard_insights()
    if insight.get("status") != "success":
        return {"status": "error", "message": insight.get("message", "Gagal ambil data insight.")}

    po_draft = purchasing_usecase.draft_purchase_orders()

    filename = f"insight-report-{insight['as_of_date']}.csv"
    filepath = os.path.join(REPORTS_DIR, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow(["== Restock Alert =="])
        writer.writerow(["Item Number", "Product Name", "SOH", "Safety Stock", "Days to Stockout"])
        for r in insight["restock_alerts"]:
            writer.writerow([r["item_number"], r["product_name"], r["soh"], r["safety_stock"], r["days_to_stockout"]])

        writer.writerow([])
        writer.writerow(["== Trending Up =="])
        writer.writerow(["Item Number", "Product Name", "Trend %"])
        for r in insight["trending_up"]:
            writer.writerow([r["item_number"], r["product_name"], r["trend_pct"]])

        writer.writerow([])
        writer.writerow(["== Trending Down =="])
        writer.writerow(["Item Number", "Product Name", "Trend %"])
        for r in insight["trending_down"]:
            writer.writerow([r["item_number"], r["product_name"], r["trend_pct"]])

        writer.writerow([])
        writer.writerow(["== Draft Purchase Order =="])
        if po_draft.get("status") == "success":
            writer.writerow(["Item Number", "Product Name", "Order Qty", "Last Price", "Estimated Cost"])
            for i in po_draft["items"]:
                writer.writerow([i["item_number"], i["product_name"], i["order_qty"], i["last_price"], i["estimated_cost"]])
        else:
            writer.writerow([po_draft.get("message", "Tidak ada draft PO.")])

    return {"status": "success", "filename": filename}
