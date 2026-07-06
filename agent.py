from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
import stock_manager
import transaction_manager
import analytics
import os

# ---------------------------------------------------------------------------
# Tools (grouped by the domain of the agent that owns them)
# ---------------------------------------------------------------------------

@tool("Check Stock")
def check_stock_tool(item_query: str) -> str:
    """Useful to check the available stock (SOH) of a sparepart. Input should be the item name or number."""
    return stock_manager.check_stock(item_query)

@tool("Get Low Stock Items")
def low_stock_tool(dummy: str) -> str:
    """Useful to find items that are low in stock, warning, or danger. Input can be anything (e.g. 'none')."""
    return stock_manager.get_low_stock_items()

@tool("View Outgoing Stock")
def outgoing_stock_tool(department: str = None) -> str:
    """Useful to view recent outgoing stock transactions. Input can be an empty string or a department name to filter by."""
    if department and department.lower() == "none":
        department = None
    return transaction_manager.view_outgoing_stock(department)

@tool("Get Top Users of Item")
def top_users_tool(item_query: str) -> str:
    """Useful to find who uses a sparepart the most. Input should be the item name or number."""
    return transaction_manager.get_top_users_of_item(item_query)

@tool("Analyze Sparepart Trend")
def analyze_trend_tool(item_query: str) -> str:
    """Useful to analyze average daily usage and basic trends. Input should be the item name or number."""
    return analytics.analyze_sparepart_trend(item_query)

@tool("Predict Monthly Needs")
def predict_needs_tool(item_query: str) -> str:
    """Useful to statistically predict how many units of an item will be needed in the next 30 days. Input should be the item name or number."""
    return analytics.predict_monthly_needs(item_query)

# ---------------------------------------------------------------------------
# LLM selection
# ---------------------------------------------------------------------------

from dotenv import load_dotenv
load_dotenv()

llm_provider = os.getenv("LLM_PROVIDER", "ollama").lower()

if llm_provider == "gemini":
    selected_llm = LLM(
        model="gemini/gemini-2.5-flash",
        temperature=0.5
    )
else:
    selected_llm = LLM(
        model="ollama/llama3.1",
        base_url="http://localhost:11434"
    )

# ---------------------------------------------------------------------------
# Specialist agents (each owns one domain of tools)
# ---------------------------------------------------------------------------

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
    goal="Analyze usage trends and statistically forecast future monthly needs for a sparepart.",
    backstory="You are a supply chain data scientist who uses historical transaction data and "
              "Prophet-based forecasting to project future demand. You only answer using the "
              "Analyze Sparepart Trend and Predict Monthly Needs tools.",
    verbose=True,
    allow_delegation=False,
    llm=selected_llm,
    tools=[analyze_trend_tool, predict_needs_tool],
)

specialist_agents = [stock_agent, transaction_agent, analytics_agent]

# ---------------------------------------------------------------------------
# Query entrypoint — a Manager agent (auto-created by CrewAI via manager_llm)
# delegates the task to whichever specialist(s) are relevant.
# ---------------------------------------------------------------------------

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
    crew = _build_crew(user_query)
    result = crew.kickoff()
    return str(result)

async def process_user_query(user_query: str) -> str:
    """
    Async entrypoint kept for direct/non-queued use of the CrewAI crew.
    """
    crew = _build_crew(user_query)
    result = await crew.kickoff_async()
    return str(result)
