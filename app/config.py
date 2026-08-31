import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

DB_NAME = "sparepart.db"

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Chat id tujuan buat notifikasi otomatis (restock alert dari Celery beat).
# Beda sama TELEGRAM_TOKEN punya bot-nya, ini id chat/group yang mau dikirimin.
TELEGRAM_ALERT_CHAT_ID = os.getenv("TELEGRAM_ALERT_CHAT_ID")

REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")


GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Ensure LiteLLM uses Google Gemini v1beta endpoint where gemini-1.5-flash / gemini-2.0 is supported
os.environ.setdefault("GEMINI_API_VERSION", "v1beta")


def build_llm() -> LLM:
    """Build the CrewAI LLM client for whichever provider is configured in .env."""

    if LLM_PROVIDER == "gemini":
        model_name = GEMINI_MODEL if GEMINI_MODEL.startswith("gemini/") else f"gemini/{GEMINI_MODEL}"
        return LLM(model=model_name, api_version="v1beta", temperature=0.5)
        
    return LLM(model="ollama/llama3.1", base_url="http://localhost:11434")


