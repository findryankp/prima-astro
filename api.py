"""Entrypoint for `uvicorn api:app --reload`. Actual app lives in app/delivery/http/api.py."""
from app.delivery.http.api import app
