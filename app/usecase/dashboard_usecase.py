import pandas as pd
from app.repository import sparepart_repository, transaction_repository


def get_stats() -> dict:
    stats = sparepart_repository.get_dashboard_stats()
    return {
        "total_items": stats["total_items"],
        "low_stock_items": stats["low_stock_items"],
        "total_transactions": transaction_repository.count_all(),
    }


def _to_json_records(df: pd.DataFrame) -> list:
    return df.where(pd.notnull(df), None).to_dict(orient="records")


def get_low_stock_table() -> list:
    df = sparepart_repository.get_low_stock(limit=10)
    return _to_json_records(df)


def get_recent_transactions() -> list:
    df = transaction_repository.get_outgoing(department=None, limit=10)
    return _to_json_records(df)


def get_items_list() -> list:
    df = sparepart_repository.get_items_with_tx_count()
    return _to_json_records(df)
