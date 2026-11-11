# Personal Finance Analyzer

Python project that analyzes financial transactions to calculate **income, expenses, savings**
and **spending patterns**, with auto-categorization, anomaly detection, expense forecasting,
budget tracking and a financial health score.

## Features
| Feature | Module |
|---|---|
| CSV loading, validation, cleaning | `src/data_loader.py` |
| Keyword auto-categorization | `src/categorizer.py` |
| Income / expense / savings, monthly & category analysis, recurring bills, budgets, health score | `src/analysis.py` |
| Unusual-transaction detection (z-score per category) | `src/anomaly.py` |
| 3-month expense forecast (linear trend + moving average) | `src/forecast.py` |
| Dashboard image + Markdown report | `src/report.py` |
| Interactive web dashboard | `app.py` (Streamlit) |
| Unit tests | `tests/` |

## Setup
```bash
pip install -r requirements.txt
python generate_data.py          # creates data/sample_transactions.csv
```

## Run
```bash
python main.py                              # CLI analysis on sample data
python main.py --input my_data.csv          # your own data
streamlit run app.py                        # interactive dashboard
python -m pytest -q                         # run tests
```
Outputs are saved in `reports/` (`dashboard.png`, `report.md`, CSV tables).

## Input format
CSV with columns `date, description, amount` (optional `category`).
`amount > 0` = income, `amount < 0` = expense. Missing categories are filled automatically.

## Method
- **Savings rate** = (income - expenses) / income x 100
- **Health score (0-100)**: savings rate 40 + months in surplus 20 + emergency cushion 20 + spending stability 20
- **Anomalies**: expense with z-score > 2.5 inside its category (min 5 transactions)
- **Recurring**: same description in 3+ months with amount variation <= 15%
- **Forecast**: `numpy.polyfit` linear trend on monthly expenses

## Sample results (sample data)
Income 54,732 | Expenses 35,546 | Savings 19,185 (35.1%) | Health score 93.5 (A)
Rent = 47% of spending; Shopping is over a 150/month budget; 2 unusual purchases detected.

## Project structure
```
finance_analyzer/
├── app.py  main.py  generate_data.py  requirements.txt  README.md
├── src/    categorizer.py data_loader.py analysis.py anomaly.py forecast.py report.py
├── tests/  test_analysis.py
├── data/   sample_transactions.csv
└── reports/ dashboard.png report.md *.csv
```

## Future work
Machine-learning categorization, bank API integration, multi-currency support, savings-goal tracking.
