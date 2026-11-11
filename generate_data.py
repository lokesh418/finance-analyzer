"""Generate a realistic sample dataset (data/sample_transactions.csv)."""
import numpy as np
import pandas as pd


def generate(path="data/sample_transactions.csv", seed=7):
    rng = np.random.default_rng(seed)
    rows = []
    for m in pd.date_range("2025-01-01", periods=12, freq="MS"):
        d = lambda n: m + pd.Timedelta(days=int(n))
        rows.append((d(0), "ACME Corp Salary", "", 4500))
        if rng.random() < 0.35:
            rows.append((d(14), "Freelance Payment", "Freelance", int(rng.integers(300, 900))))
        rows.append((d(1), "Landlord Rent", "Rent", -1400))
        rows.append((d(5), "Electric Company", "", -round(rng.uniform(70, 130), 2)))
        rows.append((d(6), "Internet Provider", "", -59.99))
        rows.append((d(9), "Netflix", "", -15.99))
        rows.append((d(9), "Spotify", "", -10.99))
        rows.append((d(3), "Gym Membership", "", -35.00))
        for _ in range(rng.integers(8, 13)):
            rows.append((d(rng.integers(0, 28)), str(rng.choice(["Whole Foods", "Trader Joes"])),
                         "", -round(rng.uniform(25, 110), 2)))
        for _ in range(rng.integers(3, 7)):
            rows.append((d(rng.integers(0, 28)), str(rng.choice(["Restaurant", "Starbucks"])),
                         "", -round(rng.uniform(6, 70), 2)))
        for _ in range(rng.integers(2, 5)):
            rows.append((d(rng.integers(0, 28)), str(rng.choice(["Uber", "Shell Gas"])),
                         "", -round(rng.uniform(15, 60), 2)))
        for _ in range(rng.integers(1, 4)):
            rows.append((d(rng.integers(0, 28)), "Amazon", "", -round(rng.uniform(20, 120), 2)))
        if rng.random() < 0.4:
            rows.append((d(rng.integers(0, 28)), "Pharmacy", "", -round(rng.uniform(10, 45), 2)))
    # deliberate anomalies for detection demo
    rows.append((pd.Timestamp("2025-07-18"), "Laptop Purchase", "Shopping", -1800))
    rows.append((pd.Timestamp("2025-10-22"), "Emergency Car Repair", "Transport", -950))
    df = pd.DataFrame(rows, columns=["date", "description", "category", "amount"])
    df.sort_values("date").to_csv(path, index=False, date_format="%Y-%m-%d")
    return path


if __name__ == "__main__":
    print("Created", generate())
