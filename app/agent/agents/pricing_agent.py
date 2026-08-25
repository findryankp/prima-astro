from crewai import Agent
from app.agent.tools import price_insight_tool, estimate_item_price_tool


def build_pricing_agent(llm) -> Agent:
    return Agent(
        role="Cost Insight Specialist",
        goal="Answer questions about item pricing and how much value is currently tied up in stock.",
        backstory="You are a cost analyst who looks at last purchase prices and stock levels to answer "
                  "'how much is this worth' type questions. You only answer using the Get Price Insights "
                  "and Estimate Item Price tools.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[price_insight_tool, estimate_item_price_tool],
    )
