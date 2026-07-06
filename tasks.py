from celery_app import celery_app
from agent import process_user_query_sync

@celery_app.task(name="tasks.process_query_task")
def process_query_task(user_query: str) -> str:
    """
    Celery task executed by the worker process. Runs the CrewAI crew
    synchronously since Celery workers operate outside an asyncio event loop.
    """
    return process_user_query_sync(user_query)
