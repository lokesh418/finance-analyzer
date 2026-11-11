"""Forecast future monthly expenses with a linear trend + moving average."""
import numpy as np
import pandas as pd
from .analysis import monthly_table


def forecast_expenses(df: pd.DataFrame, periods: int = 3) -> pd.DataFrame:
    m = monthly_table(df)
    if len(m) < 3:
        raise ValueError("Need at least 3 months of data to forecast.")
    y = m["Expense"].values
    x = np.arange(len(y))
    slope, intercept = np.polyfit(x, y, 1)
    last = pd.Period(m.index[-1], freq="M")
    rows = []
    for i in range(1, periods + 1):
        rows.append({"month": str(last + i),
                     "linear_forecast": round(float(intercept + slope * (len(y) - 1 + i)), 2),
                     "moving_avg_forecast": round(float(y[-3:].mean()), 2)})
    out = pd.DataFrame(rows).set_index("month")
    out.attrs["trend_per_month"] = round(float(slope), 2)
    return out
