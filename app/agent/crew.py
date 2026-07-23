from crewai import Agent, Task, Crew, Process
from app.config import build_llm
from app.agent.tools import (
    check_stock_tool,
    low_stock_tool,
    outgoing_stock_tool,
    top_users_tool,
    analyze_trend_tool,
    predict_needs_tool,
    dashboard_insights_tool,
)

selected_llm = build_llm()

stock_agent = Agent(
    role="Stock Specialist",
    goal="Report accurate current stock levels (SOH) and flag items that are low, warning, or danger.",
    backstory="You are an inventory clerk who knows the warehouse stock sheet by heart. "
              "You only answer using the Check Stock and Get Low Stock Items tools. Never guess a number.",
    verbose=True,
    allow_delegation=False,
    llm=selected_llm,
    tools=[check_stock_tool, low_stock_tool],
)

transaction_agent = Agent(
    role="Transaction Specialist",
    goal="Report outgoing stock history and identify which department or PIC uses an item the most.",
    backstory="You are a logistics analyst who tracks every outgoing transaction. "
              "You only answer using the View Outgoing Stock and Get Top Users of Item tools.",
    verbose=True,
    allow_delegation=False,
    llm=selected_llm,
    tools=[outgoing_stock_tool, top_users_tool],
)

analytics_agent = Agent(
    role="Analytics Specialist",
    goal="Analyze usage trends and statistically forecast future monthly needs for a sparepart, "
         "and surface catalog-wide restock/trend insights.",
    backstory="You are a supply chain data scientist who uses historical transaction data and "
              "Prophet-based forecasting to project future demand. You only answer using the "
              "Analyze Sparepart Trend, Predict Monthly Needs, and Get Dashboard Insights tools.",
    verbose=True,
    allow_delegation=False,
    llm=selected_llm,
    tools=[analyze_trend_tool, predict_needs_tool, dashboard_insights_tool],
)

specialist_agents = [stock_agent, transaction_agent, analytics_agent]


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
