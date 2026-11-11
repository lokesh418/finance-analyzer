"""Load, validate and clean transaction data."""
import numpy as np
import pandas as pd
from .categorizer import categorize

REQUIRED = ["date", "description", "amount"]


def load_transactions(source) -> pd.DataFrame:
    """source: file path or file-like object (e.g. Streamlit upload).
    amount > 0 is income, amount < 0 is an expense."""
    df = pd.read_csv(source)
    df.columns = [c.strip().lower() for c in df.columns]

    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["date", "amount"]).drop_duplicates()
    if df.empty:
        raise ValueError("No valid rows found after cleaning.")

    df["description"] = df["description"].fillna("").astype(str)
    if "category" not in df.columns:
        df["category"] = np.nan
    df = categorize(df)

    df["type"] = np.where(df["amount"] > 0, "Income", "Expense")
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["weekday"] = df["date"].dt.day_name()
    return df.sort_values("date").reset_index(drop=True)
