from app.agent.agents.stock_agent import build_stock_agent
from app.agent.agents.transaction_agent import build_transaction_agent
from app.agent.agents.analytics_agent import build_analytics_agent
from app.agent.agents.purchasing_agent import build_purchasing_agent
from app.agent.agents.pricing_agent import build_pricing_agent


def build_all_agents(llm):
    """Satu titik masuk buat rakit semua agent spesialis, dipanggil dari crew.py."""
    return [
        build_stock_agent(llm),
        build_transaction_agent(llm),
        build_analytics_agent(llm),
        build_purchasing_agent(llm),
        build_pricing_agent(llm),
    ]
