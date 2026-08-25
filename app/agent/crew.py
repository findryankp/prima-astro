from crewai import Task, Crew, Process
from app.config import build_llm
from app.agent.agents import build_all_agents

selected_llm = build_llm()

# Tiap agent dirakit di file-nya masing-masing (app/agent/agents/*.py) supaya
# nambah spesialis baru gak perlu ngoprek file ini — tinggal daftarin di
# app/agent/agents/__init__.py.
specialist_agents = build_all_agents(selected_llm)


def _build_crew(user_query: str) -> Crew:
    task = Task(
        description=f"Answer the user's query: '{user_query}'. "
                    f"Delegate to the specialist agent(s) best suited to retrieve the data. "
                    f"Provide the final answer in a clear, conversational, and helpful manner.",
        expected_output="A helpful answer addressing the user's query with actual data.",
        agent=None,
    )

    return Crew(
        agents=specialist_agents,
        tasks=[task],
        process=Process.hierarchical,
        manager_llm=selected_llm,
        verbose=True,
    )


def process_user_query_sync(user_query: str) -> str:
    """
    Synchronous entrypoint for the CrewAI crew. Intended to be called from
    within a Celery worker task (worker processes run outside an event loop).
    """
    try:
        crew = _build_crew(user_query)
        result = crew.kickoff()
        return str(result)
    except Exception as e:
        return _handle_crew_error(e)


async def process_user_query(user_query: str) -> str:
    """
    Async entrypoint kept for direct/non-queued use of the CrewAI crew.
    """
    try:
        crew = _build_crew(user_query)
        result = await crew.kickoff_async()
        return str(result)
    except Exception as e:
        return _handle_crew_error(e)

def _handle_crew_error(e: Exception) -> str:
    error_msg = str(e)
    if "API_KEY_INVALID" in error_msg or "API key not valid" in error_msg or "400 INVALID_ARGUMENT" in error_msg:
        return "🤖 **Maaf, konfigurasi AI bermasalah.**\nAPI Key (Google Gemini) yang digunakan tidak valid atau belum diatur. Silakan periksa pengaturan Gemini API Key."
    elif "Connection error" in error_msg or "localhost:11434" in error_msg:
        return "🤖 **Maaf, AI lokal tidak merespons.**\nTidak dapat terhubung ke Ollama. Pastikan aplikasi Ollama sudah berjalan."
    
    # Generic fallback human-readable error
    return f"🤖 **Maaf, terjadi kendala teknis pada sistem AI.**\nSilakan coba beberapa saat lagi. *(Detail: {error_msg[:100]}...)*"
