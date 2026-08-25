import requests
from app.config import TELEGRAM_TOKEN, TELEGRAM_ALERT_CHAT_ID
from app.usecase import analytics_usecase

TELEGRAM_API_BASE = "https://api.telegram.org"


def _build_alert_text(insight: dict) -> str | None:
    alerts = insight.get("restock_alerts", [])
    if not alerts:
        return None

    lines = [f"⚠️ Restock Alert — {insight['as_of_date']}", ""]
    for r in alerts:
        eta = f"{r['days_to_stockout']} hari lagi" if r["days_to_stockout"] is not None else "gak ketahuan kapan"
        lines.append(f"- {r['product_name']} ({r['item_number']}): sisa {r['soh']} {r['unit']}, habis ~{eta}")

    return "\n".join(lines)


def send_restock_alert() -> str:
    """
    Cek insight terbaru, dan kalau ada item yang butuh restock mendesak,
    kirim ringkasannya ke chat Telegram yang udah dikonfigurasi. Dipanggil
    periodik lewat Celery beat, jadi gudang gak perlu buka dashboard tiap
    hari cuma buat ngecek stok kritis.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_ALERT_CHAT_ID:
        return "Dilewati: TELEGRAM_TOKEN atau TELEGRAM_ALERT_CHAT_ID belum diisi di .env."

    insight = analytics_usecase.get_dashboard_insights()
    if insight.get("status") != "success":
        return f"Dilewati: gagal ambil insight ({insight.get('message', 'unknown error')})."

    text = _build_alert_text(insight)
    if text is None:
        return "Gak ada item kritis hari ini, notifikasi gak dikirim."

    url = f"{TELEGRAM_API_BASE}/bot{TELEGRAM_TOKEN}/sendMessage"
    resp = requests.post(url, json={"chat_id": TELEGRAM_ALERT_CHAT_ID, "text": text}, timeout=15)
    resp.raise_for_status()
    return "Notifikasi restock terkirim ke Telegram."
