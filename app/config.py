import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

DB_NAME = "sparepart.db"

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


def build_llm() -> LLM:
    """Build the CrewAI LLM client for whichever provider is configured in .env."""
    if LLM_PROVIDER == "gemini":
        return LLM(model="gemini/gemini-2.5-flash", temperature=0.5)
    return LLM(model="ollama/llama3.1", base_url="http://localhost:11434")
