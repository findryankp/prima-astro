from crewai import Agent
from app.agent.tools import outgoing_stock_tool, top_users_tool


def build_transaction_agent(llm) -> Agent:
    return Agent(
        role="Transaction Specialist",
        goal="Report outgoing stock history and identify which department or PIC uses an item the most.",
        backstory="You are a logistics analyst who tracks every outgoing transaction. "
                  "You only answer using the View Outgoing Stock and Get Top Users of Item tools.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[outgoing_stock_tool, top_users_tool],
    )
