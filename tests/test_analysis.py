import io
import pandas as pd
import pytest
from src.data_loader import load_transactions
from src import analysis as an
from src.anomaly import detect_anomalies
from src.forecast import forecast_expenses
from src.categorizer import guess_category

CSV = """date,description,category,amount
2025-01-01,ACME Salary,,3000
2025-01-02,Landlord Rent,,-1000
2025-01-05,Whole Foods,,-200
2025-02-01,ACME Salary,,3000
2025-02-02,Landlord Rent,,-1000
2025-02-06,Whole Foods,,-250
2025-03-01,ACME Salary,,3000
2025-03-02,Landlord Rent,,-1000
2025-03-07,Whole Foods,,-300
"""


@pytest.fixture
def df():
    return load_transactions(io.StringIO(CSV))


def test_summary(df):
    s = an.summary(df)
    assert s["total_income"] == 9000
    assert s["total_expenses"] == 3750
    assert s["net_savings"] == 5250
    assert round(s["savings_rate"], 2) == 58.33


def test_categorizer():
    assert guess_category("Netflix subscription") == "Entertainment"
    assert guess_category("???") == "Other"


def test_auto_category(df):
    assert set(df["category"]) == {"Salary", "Rent", "Groceries"}


def test_monthly_table(df):
    m = an.monthly_table(df)
    assert list(m.index) == ["2025-01", "2025-02", "2025-03"]
    assert m.loc["2025-02", "Expense"] == 1250


def test_recurring(df):
    assert "Landlord Rent" in an.recurring_expenses(df).index


def test_forecast_needs_data(df):
    assert len(forecast_expenses(df)) == 3
    with pytest.raises(ValueError):
        forecast_expenses(df[df["month"] == "2025-01"])


def test_anomaly_detection():
    rows = ["date,description,category,amount"]
    for i in range(10):
        rows.append(f"2025-01-{i+1:02d},Amazon,,-50")
    rows.append("2025-01-20,Amazon,,-2000")
    d = load_transactions(io.StringIO("\n".join(rows)))
    out = detect_anomalies(d)
    assert len(out) == 1 and out.loc[0, "spend"] == 2000


def test_missing_columns():
    with pytest.raises(ValueError):
        load_transactions(io.StringIO("date,amount\n2025-01-01,5"))


def test_health_score_range(df):
    h = an.health_score(df)
    assert 0 <= h["score"] <= 100 and h["grade"] in "ABCDF"
