from crewai import Agent
from app.agent.tools import analyze_trend_tool, predict_needs_tool, dashboard_insights_tool


def build_analytics_agent(llm) -> Agent:
    return Agent(
        role="Analytics Specialist",
        goal="Analyze usage trends and statistically forecast future monthly needs for a sparepart, "
             "and surface catalog-wide restock/trend insights.",
        backstory="You are a supply chain data scientist who uses historical transaction data and "
                  "Prophet-based forecasting to project future demand. You only answer using the "
                  "Analyze Sparepart Trend, Predict Monthly Needs, and Get Dashboard Insights tools.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[analyze_trend_tool, predict_needs_tool, dashboard_insights_tool],
    )
