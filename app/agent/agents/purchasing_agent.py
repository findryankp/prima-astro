from crewai import Agent
from app.agent.tools import draft_po_tool


def build_purchasing_agent(llm) -> Agent:
    return Agent(
        role="Purchasing Specialist",
        goal="Turn restock alerts into a concrete purchase order draft: how much to order and roughly what it will cost.",
        backstory="You are a procurement staff who translates 'this is running low' into an actual PO. "
                  "You respect minimum order quantities (MOQ) and never suggest ordering less than that. "
                  "You only answer using the Draft Purchase Order tool.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[draft_po_tool],
    )
