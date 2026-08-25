from app.delivery.worker.celery_app import celery_app
from app.agent.crew import process_user_query_sync
from app.usecase import notification_usecase, report_usecase

@celery_app.task
def process_query_task(user_query: str) -> str:
    """
    Celery task executed by the worker process. Runs the CrewAI crew
    synchronously since Celery workers operate outside an asyncio event loop.
    """
    return process_user_query_sync(user_query)


@celery_app.task
def send_restock_alert_task() -> str:
    """Dipanggil sama Celery beat tiap pagi buat ngecek stok kritis dan kirim alert ke Telegram."""
    return notification_usecase.send_restock_alert()


@celery_app.task
def generate_report_task() -> dict:
    """Bikin CSV insight report di background, dipanggil dari endpoint /api/reports/generate."""
    return report_usecase.generate_insight_report()
