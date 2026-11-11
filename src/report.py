"""Create the dashboard image and a Markdown report."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from . import analysis as an
from .anomaly import detect_anomalies
from .forecast import forecast_expenses


def make_dashboard(df, path):
    m, cat = an.monthly_table(df), an.category_breakdown(df)
    wd = an.weekday_pattern(df)
    fig, ax = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("Personal Finance Dashboard", fontsize=18, fontweight="bold")

    # --- backgrounds: soft gradient behind white chart panels ---
    bg = fig.add_axes([0, 0, 1, 1], zorder=-10)
    bg.axis("off")
    grad = np.linspace(0, 1, 256).reshape(1, -1)
    bg.imshow(grad, aspect="auto", extent=[0, 1, 0, 1],
              cmap=LinearSegmentedColormap.from_list("bg", ["#eef3fb", "#e6eefb", "#f3ecfb"]))
    for a in ax.flat:
        a.set_facecolor("white")
        for sp in a.spines.values():
            sp.set_color("#d5dcec")
    x = list(range(len(m)))

    ax[0, 0].bar([i - 0.2 for i in x], m["Income"], 0.4, label="Income", color="#2e8b57")
    ax[0, 0].bar([i + 0.2 for i in x], m["Expense"], 0.4, label="Expense", color="#cd5c5c")
    ax[0, 0].set_xticks(x)
    ax[0, 0].set_xticklabels(m.index, rotation=60, fontsize=8)
    ax[0, 0].set_title("Monthly Income vs Expenses")
    ax[0, 0].legend()

    ax[0, 1].plot(list(m.index), m["Savings"].cumsum().values, marker="o", color="#4169e1")
    ax[0, 1].set_title("Cumulative Savings")
    ax[0, 1].grid(alpha=.3)
    ax[0, 1].tick_params(axis="x", rotation=60, labelsize=8)

    ax[0, 2].pie(cat["sum"], labels=cat.index, autopct="%1.0f%%", startangle=90,
                 textprops={"fontsize": 8})
    ax[0, 2].set_title("Spending by Category")

    ax[1, 0].bar(wd.index, wd.values, color="#daa520")
    ax[1, 0].set_title("Spending by Weekday")
    ax[1, 0].tick_params(axis="x", rotation=45, labelsize=8)

    ax[1, 1].plot(list(m.index), m["Savings Rate %"].values, marker="s", color="#8a2be2")
    ax[1, 1].axhline(20, ls="--", color="gray", label="20% target")
    ax[1, 1].set_title("Monthly Savings Rate (%)")
    ax[1, 1].legend()
    ax[1, 1].tick_params(axis="x", rotation=60, labelsize=8)

    labels = list(m.index)
    ax[1, 2].plot(range(len(m)), m["Expense"].values, marker="o",
                  label="Actual", color="#cd5c5c")
    try:
        f = forecast_expenses(df)
        labels += list(f.index)
        ax[1, 2].plot(range(len(m), len(labels)), f["linear_forecast"].values,
                      "o--", color="#ff8c00", label="Forecast")
    except ValueError:
        pass
    ax[1, 2].set_xticks(range(len(labels)))
    ax[1, 2].set_xticklabels(labels, rotation=60, fontsize=8)
    ax[1, 2].set_title("Expense Forecast")
    ax[1, 2].legend()

    plt.tight_layout()
    fig.savefig(path, dpi=110, facecolor=fig.get_facecolor())
    plt.close(fig)


def write_markdown(df, path):
    s, h = an.summary(df), an.health_score(df)
    m, cat = an.monthly_table(df), an.category_breakdown(df)
    L = ["# Financial Analysis Report", "",
         f"Period: {df['date'].min().date()} to {df['date'].max().date()} "
         f"({s['months']} months, {s['transactions']} transactions)", "",
         "## Summary",
         f"- Total income: **{s['total_income']:,.2f}**",
         f"- Total expenses: **{s['total_expenses']:,.2f}**",
         f"- Net savings: **{s['net_savings']:,.2f}**",
         f"- Savings rate: **{s['savings_rate']:.1f}%**", "",
         f"## Financial Health Score: {h['score']}/100 (Grade {h['grade']})"]
    L += [f"- {k}: {v}" for k, v in h["components"].items()]
    L += ["", "## Spending by Category", "```", cat.to_string(), "```",
          "", "## Monthly Table", "```", m.to_string(), "```", ""]
    rec = an.recurring_expenses(df)
    if not rec.empty:
        L += ["## Recurring Expenses", "```", rec.to_string(), "```", ""]
    anom = detect_anomalies(df)
    if not anom.empty:
        L += ["## Unusual Transactions", "```", anom.to_string(index=False), "```", ""]
    try:
        f = forecast_expenses(df)
        L += ["## Expense Forecast (next 3 months)", "```", f.to_string(), "```",
              f"Trend: {f.attrs['trend_per_month']:+,.2f} per month", ""]
    except ValueError:
        pass
    with open(path, "w") as fh:
        fh.write("\n".join(L))
