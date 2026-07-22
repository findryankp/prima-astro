import pandas as pd
import numpy as np
from prophet import Prophet
from app.repository import transaction_repository, sparepart_repository


def analyze_sparepart_trend(item_query: str, days: int = 30) -> str:
    """Analyze the outgoing trend for a specific sparepart over the last X days."""
    df = transaction_repository.get_for_item(item_query)

    if df.empty:
        return f"No trend data available for '{item_query}'."

    df["tanggal"] = pd.to_datetime(df["tanggal"])
    product_name = df["product_name"].iloc[0]

    cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=days)
    recent_df = df[df["tanggal"] >= cutoff_date]

    if recent_df.empty:
        return f"No usage found for '{product_name}' in the last {days} days. Total lifetime usage: {df['qty_out'].sum()}."

    total_used = recent_df["qty_out"].sum()
    avg_daily = total_used / days

    result = f"Trend Analysis for '{product_name}' (Last {days} days):\n"
    result += f"- Total Outgoing: {total_used} units\n"
    result += f"- Average Daily Usage: {avg_daily:.2f} units/day\n"
    result += f"- Projected Monthly Need (30 days): {avg_daily * 30:.2f} units\n"
    return result


def predict_monthly_needs(item_query: str) -> str:
    """Predict future monthly needs using Facebook Prophet (basic setup)."""
    df = transaction_repository.get_for_item(item_query)

    if df.empty or len(df) < 5:
        return f"Not enough historical data to forecast for '{item_query}'. Need at least 5 transactions."

    df["tanggal"] = pd.to_datetime(df["tanggal"])
    daily_data = df.groupby(df["tanggal"].dt.date)["qty_out"].sum().reset_index()
    daily_data.columns = ["ds", "y"]

    try:
        m = Prophet(daily_seasonality=False, yearly_seasonality=False)
        m.fit(daily_data)

        future = m.make_future_dataframe(periods=30)
        forecast = m.predict(future)

        future_forecast = forecast[forecast["ds"] > pd.Timestamp.now()]
        predicted_total = max(0, future_forecast["yhat"].sum())
        product_name = df["product_name"].iloc[0]

        result = f"Prediction for '{product_name}' (Next 30 Days):\n"
        result += f"- Forecasted Need: {predicted_total:.2f} units\n"
        result += "(Note: This is a statistical prediction based on historical trends using Prophet.)"
        return result
    except Exception as e:
        return f"Error running forecast: {str(e)}. (Fallback: Try 'analyze_sparepart_trend' instead)"


def get_forecast_data(item_query: str) -> dict:
    """Generate a Prophet forecast and return raw data (dates, actuals, predicted) for charting."""
    df = transaction_repository.get_for_item(item_query)

    if df.empty or len(df) < 5:
        return {"status": "error", "message": "Not enough historical data to forecast. Need at least 5 transactions."}

    df["tanggal"] = pd.to_datetime(df["tanggal"])
    daily_data = df.groupby(df["tanggal"].dt.date)["qty_out"].sum().reset_index()
    daily_data.columns = ["ds", "y"]

    try:
        m = Prophet(daily_seasonality=False, yearly_seasonality=False)
        m.fit(daily_data)

        future = m.make_future_dataframe(periods=30)
        forecast = m.predict(future)

        historical = daily_data.copy()
        historical["ds"] = historical["ds"].astype(str)

        forecast_res = forecast[["ds", "yhat"]].copy()
        forecast_res["yhat"] = forecast_res["yhat"].clip(lower=0)
        forecast_res["ds"] = forecast_res["ds"].dt.strftime("%Y-%m-%d")

        merged = pd.merge(forecast_res, historical, on="ds", how="left")

        return {
            "status": "success",
            "product_name": df["product_name"].iloc[0],
            "dates": merged["ds"].tolist(),
            "actual": [None if pd.isna(v) else float(v) for v in merged["y"]],
            "predicted": [None if pd.isna(v) else round(float(v), 2) for v in merged["yhat"]],
        }
    except Exception as e:
        return {"status": "error", "message": f"Error running forecast: {str(e)}"}


def get_dashboard_insights(window_days: int = 30, restock_lead_time_days: int = 14, top_n: int = 8) -> dict:
    """
    Batch AI insight for the whole catalog: for every item, project a
    naive/moving-average 30-day demand forecast, a period-over-period trend
    (last `window_days` vs the previous `window_days`), and an estimated
    days-until-stockout.

    Algorithm: moving-average forecasting + period-over-period trend
    comparison, not Prophet. Prophet is fit per-item and is too slow to run
    across an entire catalog on every dashboard load, and most items don't
    have the 5+ transactions Prophet needs. A moving average is cheap enough
    to batch-score every item at once and degrades gracefully with sparse
    data, which is what a fast, always-on dashboard panel needs. Prophet
    stays reserved for the deep-dive, on-demand single-item Forecasting page
    (see get_forecast_data above).
    """
    tx = transaction_repository.get_all()
    items = sparepart_repository.get_all()

    if tx.empty or items.empty:
        return {"status": "error", "message": "No data available to generate insights."}

    tx["tanggal"] = pd.to_datetime(tx["tanggal"])

    # Anchor on the latest transaction date in the data (not wall-clock "now")
    # so insights stay meaningful even if the DB hasn't been synced recently.
    as_of = tx["tanggal"].max()
    recent_start = as_of - pd.Timedelta(days=window_days)
    prev_start = as_of - pd.Timedelta(days=2 * window_days)

    recent = tx[tx["tanggal"] > recent_start].groupby("item_number")["qty_out"].sum()
    previous = tx[(tx["tanggal"] > prev_start) & (tx["tanggal"] <= recent_start)].groupby("item_number")["qty_out"].sum()

    stats = items.set_index("item_number").copy()
    stats["recent_total"] = recent
    stats["previous_total"] = previous
    stats[["recent_total", "previous_total"]] = stats[["recent_total", "previous_total"]].fillna(0.0)

    stats["avg_daily_usage"] = stats["recent_total"] / window_days
    stats["forecast_30d_need"] = (stats["avg_daily_usage"] * 30).round(1)

    stats["days_to_stockout"] = np.where(
        stats["avg_daily_usage"] > 0,
        (stats["soh"] / stats["avg_daily_usage"]).round(1),
        np.nan,
    )

    with np.errstate(divide="ignore", invalid="ignore"):
        pct_change = np.where(
            stats["previous_total"] > 0,
            (stats["recent_total"] - stats["previous_total"]) / stats["previous_total"] * 100,
            np.where(stats["recent_total"] > 0, 100.0, 0.0),
        )
    stats["trend_pct"] = np.round(pct_change, 1)

    stats = stats.reset_index()

    at_risk = stats[
        (stats["avg_daily_usage"] > 0)
        & ((stats["soh"] <= stats["safety_stock"]) | (stats["days_to_stockout"] <= restock_lead_time_days))
    ].sort_values("days_to_stockout", ascending=True).head(top_n)

    trending_up = stats[stats["recent_total"] > 0].sort_values("trend_pct", ascending=False).head(top_n)
    trending_down = stats[stats["previous_total"] > 0].sort_values("trend_pct", ascending=True).head(top_n)

    def to_records(df):
        return df.replace({np.nan: None}).to_dict(orient="records")

    return {
        "status": "success",
        "as_of_date": str(as_of.date()),
        "window_days": window_days,
        "total_forecasted_demand_30d": round(float(stats["forecast_30d_need"].sum()), 1),
        "restock_alerts": to_records(at_risk[["item_number", "product_name", "soh", "safety_stock", "unit", "avg_daily_usage", "days_to_stockout"]]),
        "trending_up": to_records(trending_up[["item_number", "product_name", "recent_total", "previous_total", "trend_pct"]]),
        "trending_down": to_records(trending_down[["item_number", "product_name", "recent_total", "previous_total", "trend_pct"]]),
    }
