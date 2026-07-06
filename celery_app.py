import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "agenticai",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["tasks"],
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
