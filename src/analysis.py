"""Core financial analysis: summary, trends, patterns, budgets, health score."""
import numpy as np
import pandas as pd

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"]


def expenses(df: pd.DataFrame) -> pd.DataFrame:
    out = df[df["amount"] < 0].copy()
    out["spend"] = -out["amount"]
    return out


def summary(df: pd.DataFrame) -> dict:
    income = float(df.loc[df["amount"] > 0, "amount"].sum())
    spent = float(-df.loc[df["amount"] < 0, "amount"].sum())
    net = income - spent
    return {
        "total_income": income,
        "total_expenses": spent,
        "net_savings": net,
        "savings_rate": (net / income * 100) if income else 0.0,
        "transactions": int(len(df)),
        "months": int(df["month"].nunique()),
    }


def monthly_table(df: pd.DataFrame) -> pd.DataFrame:
    m = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0.0)
    for col in ("Income", "Expense"):
        if col not in m:
            m[col] = 0.0
    m["Expense"] = -m["Expense"]
    m["Savings"] = m["Income"] - m["Expense"]
    m["Savings Rate %"] = (m["Savings"] / m["Income"].replace(0, np.nan) * 100).round(1)
    return m[["Income", "Expense", "Savings", "Savings Rate %"]]


def category_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    exp = expenses(df)
    cat = exp.groupby("category")["spend"].agg(["sum", "mean", "count"])
    cat["% of spending"] = (cat["sum"] / cat["sum"].sum() * 100).round(1)
    return cat.sort_values("sum", ascending=False).round(2)


def weekday_pattern(df: pd.DataFrame) -> pd.Series:
    return expenses(df).groupby("weekday")["spend"].sum().reindex(WEEKDAYS).fillna(0)


def top_merchants(df: pd.DataFrame, n: int = 5) -> pd.Series:
    return expenses(df).groupby("description")["spend"].sum().nlargest(n).round(2)


def recurring_expenses(df: pd.DataFrame, min_months: int = 3,
                       max_cv: float = 0.15) -> pd.DataFrame:
    """Expenses that appear in >= min_months with a stable amount (subscriptions, rent)."""
    g = expenses(df).groupby("description").agg(
        months=("month", "nunique"), avg_amount=("spend", "mean"),
        std=("spend", "std"), total=("spend", "sum"))
    g["std"] = g["std"].fillna(0)
    rec = g[(g["months"] >= min_months) & (g["std"] <= max_cv * g["avg_amount"])]
    return rec.drop(columns="std").sort_values("total", ascending=False).round(2)


def budget_report(df: pd.DataFrame, budgets: dict) -> pd.DataFrame:
    """Compare average monthly spend per category with a monthly budget."""
    n_months = max(df["month"].nunique(), 1)
    spent = expenses(df).groupby("category")["spend"].sum() / n_months
    rows = []
    for cat, limit in budgets.items():
        avg = float(spent.get(cat, 0.0))
        rows.append({"category": cat, "budget": limit, "avg_monthly_spend": round(avg, 2),
                     "difference": round(limit - avg, 2),
                     "status": "OVER BUDGET" if avg > limit else "OK"})
    return pd.DataFrame(rows)


def health_score(df: pd.DataFrame) -> dict:
    """Financial health score 0-100 from four components."""
    s, m = summary(df), monthly_table(df)
    avg_exp = m["Expense"].mean()
    rate_pts = min(max(s["savings_rate"], 0) / 20, 1) * 40            # 20%+ saving = full
    positive_pts = float((m["Savings"] > 0).mean()) * 20              # months in the green
    cushion = s["net_savings"] / avg_exp if avg_exp else 0
    cushion_pts = min(max(cushion, 0) / 6, 1) * 20                    # 6 months = full
    cv = m["Expense"].std(ddof=0) / avg_exp if avg_exp else 0
    stability_pts = max(0.0, 1 - cv / 0.5) * 20                       # steady spending
    score = round(rate_pts + positive_pts + cushion_pts + stability_pts, 1)
    grade = ("A" if score >= 80 else "B" if score >= 65 else
             "C" if score >= 50 else "D" if score >= 35 else "F")
    return {"score": score, "grade": grade,
            "components": {"Savings rate (40)": round(rate_pts, 1),
                           "Positive months (20)": round(positive_pts, 1),
                           "Emergency cushion (20)": round(cushion_pts, 1),
                           "Spending stability (20)": round(stability_pts, 1)}}
