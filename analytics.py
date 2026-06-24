import sqlite3
import pandas as pd
from prophet import Prophet
import datetime

DB_NAME = "sparepart.db"

def analyze_sparepart_trend(item_query, days=30):
    """
    Analyze the outgoing trend for a specific sparepart over the last X days.
    """
    conn = sqlite3.connect(DB_NAME)
    query = f"%{item_query}%"
    
    # SQLite date filtering can be tricky, but we can do it in pandas if data is small
    # For now, we will pull all dates and filter
    sql = """
    SELECT tanggal, qty_out, product_name
    FROM transactions
    WHERE product_name LIKE ? OR item_number LIKE ?
    """
    
    df = pd.read_sql_query(sql, conn, params=(query, query))
    conn.close()
    
    if df.empty:
        return f"No trend data available for '{item_query}'."
        
    # Convert 'tanggal' to datetime
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    product_name = df['product_name'].iloc[0]
    
    # Filter last X days
    cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=days)
    recent_df = df[df['tanggal'] >= cutoff_date]
    
    if recent_df.empty:
        return f"No usage found for '{product_name}' in the last {days} days. Total lifetime usage: {df['qty_out'].sum()}."
        
    total_used = recent_df['qty_out'].sum()
    avg_daily = total_used / days
    
    result = f"Trend Analysis for '{product_name}' (Last {days} days):\n"
    result += f"- Total Outgoing: {total_used} units\n"
    result += f"- Average Daily Usage: {avg_daily:.2f} units/day\n"
    result += f"- Projected Monthly Need (30 days): {avg_daily * 30:.2f} units\n"
    
    return result

def predict_monthly_needs(item_query):
    """
    Predict future monthly needs using Facebook Prophet (basic setup).
    """
    conn = sqlite3.connect(DB_NAME)
    query = f"%{item_query}%"
    
    sql = """
    SELECT tanggal, qty_out, product_name
    FROM transactions
    WHERE product_name LIKE ? OR item_number LIKE ?
    """
    
    df = pd.read_sql_query(sql, conn, params=(query, query))
    conn.close()
    
    if df.empty or len(df) < 5:
        # Not enough data for forecasting
        return f"Not enough historical data to forecast for '{item_query}'. Need at least 5 transactions."
        
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    
    # Group by date
    daily_data = df.groupby(df['tanggal'].dt.date)['qty_out'].sum().reset_index()
    daily_data.columns = ['ds', 'y']  # Prophet requires 'ds' and 'y' columns
    
    # Initialize and fit Prophet
    try:
        m = Prophet(daily_seasonality=False, yearly_seasonality=False)
        m.fit(daily_data)
        
        # Predict next 30 days
        future = m.make_future_dataframe(periods=30)
        forecast = m.predict(future)
        
        # Get sum of predictions for the next 30 days
        future_forecast = forecast[forecast['ds'] > pd.Timestamp.now()]
        predicted_total = future_forecast['yhat'].sum()
        
        # Prevent negative predictions
        predicted_total = max(0, predicted_total)
        product_name = df['product_name'].iloc[0]
        
        result = f"Prediction for '{product_name}' (Next 30 Days):\n"
        result += f"- Forecasted Need: {predicted_total:.2f} units\n"
        result += "(Note: This is a statistical prediction based on historical trends using Prophet.)"
        
        return result
    except Exception as e:
        return f"Error running forecast: {str(e)}. (Fallback: Try 'analyze_sparepart_trend' instead)"

def get_forecast_data(item_query):
    """
    Generate Prophet forecast and return raw data (dates, actuals, predicted) for charting.
    """
    conn = sqlite3.connect(DB_NAME)
    query = f"%{item_query}%"
    
    sql = """
    SELECT tanggal, qty_out, product_name
    FROM transactions
    WHERE product_name LIKE ? OR item_number LIKE ?
    """
    
    df = pd.read_sql_query(sql, conn, params=(query, query))
    conn.close()
    
    if df.empty or len(df) < 5:
        return {"status": "error", "message": "Not enough historical data to forecast. Need at least 5 transactions."}
        
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    
    # Group by date
    daily_data = df.groupby(df['tanggal'].dt.date)['qty_out'].sum().reset_index()
    daily_data.columns = ['ds', 'y']
    
    try:
        m = Prophet(daily_seasonality=False, yearly_seasonality=False)
        m.fit(daily_data)
        
        # Predict next 30 days
        future = m.make_future_dataframe(periods=30)
        forecast = m.predict(future)
        
        # Format the response for Chart.js
        historical = daily_data.copy()
        historical['ds'] = historical['ds'].astype(str)
        
        forecast_res = forecast[['ds', 'yhat']].copy()
        # Prevent negative predictions
        forecast_res['yhat'] = forecast_res['yhat'].clip(lower=0)
        forecast_res['ds'] = forecast_res['ds'].dt.strftime('%Y-%m-%d')
        
        # Create continuous arrays for charting
        # Merge historical and forecast on dates
        merged = pd.merge(forecast_res, historical, on='ds', how='left')
        
        return {
            "status": "success",
            "product_name": df['product_name'].iloc[0],
            "dates": merged['ds'].tolist(),
            "actual": [None if pd.isna(v) else float(v) for v in merged['y']],
            "predicted": [None if pd.isna(v) else round(float(v), 2) for v in merged['yhat']]
        }
    except Exception as e:
        return {"status": "error", "message": f"Error running forecast: {str(e)}"}
