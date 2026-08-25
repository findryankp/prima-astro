from celery import Celery
from celery.schedules import crontab
from app.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    "agenticai",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.delivery.worker.tasks"],
)

# Route every chat query through a single dedicated queue so requests coming
# from the Web Dashboard and the Telegram Bot are processed one at a time
# (CrewAI/LLM calls are expensive and shouldn't run concurrently against
# the same rate-limited provider). Report generation and the restock alert
# don't touch an LLM, so they share the same queue without causing contention.
celery_app.conf.update(
    task_default_queue="agent_queries",
    task_track_started=True,
    worker_prefetch_multiplier=1,
)

# Jadwal buat notifikasi restock otomatis. Perlu proses `celery beat` yang
# jalan terpisah (lihat readme.md) — worker biasa gak baca schedule ini sendiri.
celery_app.conf.beat_schedule = {
    "cek-stok-kritis-tiap-pagi": {
        "task": "app.delivery.worker.tasks.send_restock_alert_task",
        "schedule": crontab(hour=7, minute=0),
    },
}
