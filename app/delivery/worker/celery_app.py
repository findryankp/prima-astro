from celery import Celery
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
# the same rate-limited provider).
celery_app.conf.update(
    task_default_queue="agent_queries",
    task_track_started=True,
    worker_prefetch_multiplier=1,
)
