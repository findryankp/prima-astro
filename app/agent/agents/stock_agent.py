from crewai import Agent
from app.agent.tools import check_stock_tool, low_stock_tool


def build_stock_agent(llm) -> Agent:
    return Agent(
        role="Stock Specialist",
        goal="Report accurate current stock levels (SOH) and flag items that are low, warning, or danger.",
        backstory="You are an inventory clerk who knows the warehouse stock sheet by heart. "
                  "You only answer using the Check Stock and Get Low Stock Items tools. Never guess a number.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[check_stock_tool, low_stock_tool],
    )
