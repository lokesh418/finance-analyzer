"""Streamlit dashboard.  Run:  streamlit run app.py"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.data_loader import load_transactions
from src import analysis as an
from src.anomaly import detect_anomalies
from src.forecast import forecast_expenses

st.set_page_config(page_title="Finance Analyzer", page_icon="💰", layout="wide")
st.title("💰 Personal Finance Analyzer")

# ---------- background styling ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef3fb 0%, #e6eefb 45%, #f3ecfb 100%);
    background-attachment: fixed;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #eaf0fa 100%);
}
[data-testid="stMetric"] {
    background: #ffffff;
    border-radius: 14px;
    padding: 14px 18px;
    box-shadow: 0 2px 10px rgba(60, 80, 140, 0.10);
}
[data-testid="stTabs"] [data-baseweb="tab-panel"] {
    background: rgba(255, 255, 255, 0.65);
    border-radius: 14px;
    padding: 16px;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------- sidebar: data ----------
st.sidebar.header("1. Data")
upload = st.sidebar.file_uploader("Upload CSV (date, description, amount[, category])",
                                  type="csv")
try:
    df = load_transactions(upload if upload else "data/sample_transactions.csv")
except FileNotFoundError:
    st.error("Sample data missing. Run `python generate_data.py` first.")
    st.stop()
except ValueError as e:
    st.error(str(e))
    st.stop()
st.sidebar.caption("Using uploaded file" if upload else "Using sample data")

# ---------- sidebar: filters ----------
st.sidebar.header("2. Filters")
lo, hi = df["date"].min().date(), df["date"].max().date()
date_range = st.sidebar.date_input("Date range", (lo, hi), min_value=lo, max_value=hi)
if len(date_range) == 2:
    df = df[(df["date"].dt.date >= date_range[0]) & (df["date"].dt.date <= date_range[1])]
cats = sorted(df["category"].unique())
chosen = st.sidebar.multiselect("Categories", cats, default=cats)
df = df[df["category"].isin(chosen)]
if df.empty:
    st.warning("No transactions match the filters.")
    st.stop()

# ---------- KPIs ----------
s, h = an.summary(df), an.health_score(df)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Income", f"{s['total_income']:,.0f}")
c2.metric("Expenses", f"{s['total_expenses']:,.0f}")
c3.metric("Net Savings", f"{s['net_savings']:,.0f}")
c4.metric("Savings Rate", f"{s['savings_rate']:.1f}%")
c5.metric("Health Score", f"{h['score']}/100", f"Grade {h['grade']}")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Overview", "Categories", "Trends & Forecast", "Anomalies", "Budget", "Data"])

with tab1:
    m = an.monthly_table(df)
    st.subheader("Monthly income vs expenses")
    st.bar_chart(m[["Income", "Expense"]])
    st.subheader("Cumulative savings")
    st.line_chart(m["Savings"].cumsum())
    st.subheader("Health score breakdown")
    st.bar_chart(pd.Series(h["components"]))
    st.subheader("Monthly table")
    st.dataframe(m, use_container_width=True)

with tab2:
    cat = an.category_breakdown(df)
    left, right = st.columns(2)
    with left:
        fig, ax = plt.subplots()
        ax.pie(cat["sum"], labels=cat.index, autopct="%1.0f%%", startangle=90)
        st.pyplot(fig)
    with right:
        st.dataframe(cat, use_container_width=True)
    st.subheader("Spending by weekday")
    st.bar_chart(an.weekday_pattern(df))
    st.subheader("Top merchants")
    st.dataframe(an.top_merchants(df, 8))
    st.subheader("Recurring expenses (subscriptions / fixed costs)")
    st.dataframe(an.recurring_expenses(df), use_container_width=True)

with tab3:
    try:
        periods = st.slider("Months to forecast", 1, 6, 3)
        f = forecast_expenses(df, periods)
        actual = an.monthly_table(df)["Expense"].rename("Actual")
        combined = pd.concat([actual, f["linear_forecast"].rename("Forecast")], axis=1)
        st.line_chart(combined)
        st.dataframe(f, use_container_width=True)
        st.info(f"Spending trend: {f.attrs['trend_per_month']:+,.2f} per month")
    except ValueError as e:
        st.warning(str(e))

with tab4:
    z = st.slider("Sensitivity (z-score threshold)", 1.5, 4.0, 2.5, 0.1)
    anom = detect_anomalies(df, z)
    if anom.empty:
        st.success("No unusual transactions found.")
    else:
        st.dataframe(anom, use_container_width=True)

with tab5:
    st.write("Set a monthly budget per category:")
    exp_cats = an.category_breakdown(df).index.tolist()
    budgets = {}
    cols = st.columns(3)
    for i, c in enumerate(exp_cats):
        budgets[c] = cols[i % 3].number_input(c, min_value=0, value=0, step=50)
    budgets = {k: v for k, v in budgets.items() if v > 0}
    if budgets:
        rep = an.budget_report(df, budgets)
        st.dataframe(rep, use_container_width=True)
        over = rep[rep["status"] == "OVER BUDGET"]
        if len(over):
            st.error("Over budget: " + ", ".join(over["category"]))
        else:
            st.success("All budgets on track!")

with tab6:
    st.dataframe(df, use_container_width=True)
    st.download_button("Download cleaned data (CSV)", df.to_csv(index=False),
                       "cleaned_transactions.csv", "text/csv")
