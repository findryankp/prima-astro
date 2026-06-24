from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
import stock_manager
import transaction_manager
import analytics
import os

# Define Tools
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

# Configure Local LLM with Ollama
local_llm = LLM(
    model="ollama/llama3.1",
    base_url="http://localhost:11434"
)

# Define Agent
sparepart_agent = Agent(
    role="Sparepart Inventory Specialist",
    goal="Provide accurate stock data, analyze trends, and predict needs based on historical transactions.",
    backstory="You are an expert in inventory management and supply chain analytics. "
              "You help users make data-driven decisions regarding stock replenishment and monitoring. "
              "You must use the provided tools to query the database. Do not guess stock values.",
    verbose=True,
    allow_delegation=False,
    llm=local_llm,
    tools=[
        check_stock_tool, 
        low_stock_tool, 
        outgoing_stock_tool, 
        top_users_tool, 
        analyze_trend_tool, 
        predict_needs_tool
    ]
)

async def process_user_query(user_query: str) -> str:
    """
    Process a user's natural language query through the CrewAI agent.
    """
    task = Task(
        description=f"Answer the user's query: '{user_query}'. "
                    f"Use appropriate tools to retrieve data. "
                    f"Provide the final answer in a clear, conversational, and helpful manner.",
        expected_output="A helpful answer addressing the user's query with actual data.",
        agent=sparepart_agent
    )
    
    crew = Crew(
        agents=[sparepart_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    result = await crew.kickoff_async()
    return str(result)
