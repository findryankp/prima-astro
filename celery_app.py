"""Entrypoint for `celery -A celery_app worker`. Actual config lives in app/delivery/worker/celery_app.py."""
from app.delivery.worker.celery_app import celery_app
