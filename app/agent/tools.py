from crewai.tools import tool
from app.usecase import stock_usecase, transaction_usecase, analytics_usecase


@tool("Check Stock")
def check_stock_tool(item_query: str) -> str:
    """Useful to check the available stock (SOH) of a sparepart. Input should be the item name or number."""
    return stock_usecase.check_stock(item_query)


@tool("Get Low Stock Items")
def low_stock_tool(dummy: str) -> str:
    """Useful to find items that are low in stock, warning, or danger. Input can be anything (e.g. 'none')."""
    return stock_usecase.get_low_stock_items()


@tool("View Outgoing Stock")
def outgoing_stock_tool(department: str = None) -> str:
    """Useful to view recent outgoing stock transactions. Input can be an empty string or a department name to filter by."""
    return transaction_usecase.view_outgoing_stock(department)


@tool("Get Top Users of Item")
def top_users_tool(item_query: str) -> str:
    """Useful to find who uses a sparepart the most. Input should be the item name or number."""
    return transaction_usecase.get_top_users_of_item(item_query)


@tool("Analyze Sparepart Trend")
def analyze_trend_tool(item_query: str) -> str:
    """Useful to analyze average daily usage and basic trends. Input should be the item name or number."""
    return analytics_usecase.analyze_sparepart_trend(item_query)


@tool("Predict Monthly Needs")
def predict_needs_tool(item_query: str) -> str:
    """Useful to statistically predict how many units of an item will be needed in the next 30 days. Input should be the item name or number."""
    return analytics_usecase.predict_monthly_needs(item_query)


@tool("Get Dashboard Insights")
def dashboard_insights_tool(dummy: str) -> str:
    """Useful to get a catalog-wide summary: items urgently needing restock, items trending up or down in usage, and total forecasted 30-day demand. Input can be anything (e.g. 'none')."""
    data = analytics_usecase.get_dashboard_insights()
    if data.get("status") != "success":
        return data.get("message", "Unable to generate insights.")

    lines = [f"Dashboard insights as of {data['as_of_date']} (based on the last {data['window_days']} days of transactions):"]
    lines.append(f"- Total forecasted demand for the next 30 days across all items: {data['total_forecasted_demand_30d']} units.")

    if data["restock_alerts"]:
        lines.append("- Items needing restock soon:")
        for r in data["restock_alerts"]:
            eta = f"{r['days_to_stockout']} days" if r["days_to_stockout"] is not None else "unknown"
            lines.append(f"  * {r['product_name']} ({r['item_number']}): SOH {r['soh']} {r['unit']}, ~{eta} until stockout.")
    else:
        lines.append("- No items are currently at urgent restock risk.")

    if data["trending_up"]:
        lines.append("- Trending up in usage:")
        for r in data["trending_up"][:5]:
            lines.append(f"  * {r['product_name']} ({r['item_number']}): +{r['trend_pct']}% vs previous period.")

    if data["trending_down"]:
        lines.append("- Trending down in usage:")
        for r in data["trending_down"][:5]:
            lines.append(f"  * {r['product_name']} ({r['item_number']}): {r['trend_pct']}% vs previous period.")

    return "\n".join(lines)
