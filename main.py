"""Command-line runner: python main.py [--input file.csv] [--out reports]"""
import argparse
import os
from src.data_loader import load_transactions
from src import analysis as an
from src.anomaly import detect_anomalies
from src.forecast import forecast_expenses
from src.report import make_dashboard, write_markdown


def main():
    p = argparse.ArgumentParser(description="Financial transaction analyzer")
    p.add_argument("--input", default="data/sample_transactions.csv")
    p.add_argument("--out", default="reports")
    a = p.parse_args()

    if not os.path.exists(a.input) and a.input.endswith("sample_transactions.csv"):
        from generate_data import generate
        os.makedirs(os.path.dirname(a.input), exist_ok=True)
        generate(a.input)
    os.makedirs(a.out, exist_ok=True)

    df = load_transactions(a.input)
    s, h = an.summary(df), an.health_score(df)

    print("\n=== SUMMARY ===")
    print(f"Period          : {df['date'].min().date()} -> {df['date'].max().date()}")
    print(f"Total Income    : {s['total_income']:>12,.2f}")
    print(f"Total Expenses  : {s['total_expenses']:>12,.2f}")
    print(f"Net Savings     : {s['net_savings']:>12,.2f}")
    print(f"Savings Rate    : {s['savings_rate']:>11.1f}%")
    print(f"\nHealth Score    : {h['score']}/100  (Grade {h['grade']})")
    for k, v in h["components"].items():
        print(f"   {k:<26}{v}")

    print("\n=== SPENDING BY CATEGORY ===")
    print(an.category_breakdown(df))
    print("\n=== TOP 5 MERCHANTS ===")
    print(an.top_merchants(df))
    print("\n=== RECURRING EXPENSES ===")
    print(an.recurring_expenses(df))
    print("\n=== UNUSUAL TRANSACTIONS ===")
    print(detect_anomalies(df).to_string(index=False))
    try:
        f = forecast_expenses(df)
        print("\n=== EXPENSE FORECAST ===")
        print(f)
        print(f"Trend: {f.attrs['trend_per_month']:+,.2f} per month")
    except ValueError as e:
        print(e)

    budgets = {"Groceries": 700, "Dining": 200, "Entertainment": 40, "Shopping": 150}
    print("\n=== BUDGET CHECK (monthly) ===")
    print(an.budget_report(df, budgets).to_string(index=False))

    an.monthly_table(df).to_csv(os.path.join(a.out, "monthly_summary.csv"))
    an.category_breakdown(df).to_csv(os.path.join(a.out, "category_summary.csv"))
    make_dashboard(df, os.path.join(a.out, "dashboard.png"))
    write_markdown(df, os.path.join(a.out, "report.md"))
    print(f"\nSaved dashboard.png, report.md and CSVs to '{a.out}/'")


if __name__ == "__main__":
    main()
