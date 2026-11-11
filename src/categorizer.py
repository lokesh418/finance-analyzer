"""Rule-based auto-categorization of transactions from their description."""
import pandas as pd

KEYWORDS = {
    "Salary": ["salary", "payroll"],
    "Freelance": ["freelance"],
    "Rent": ["rent", "landlord"],
    "Groceries": ["whole foods", "trader", "supermarket", "grocery"],
    "Dining": ["restaurant", "starbucks", "cafe", "pizza"],
    "Transport": ["uber", "shell", "gas", "fuel", "metro", "car repair"],
    "Utilities": ["electric", "internet", "water", "utility"],
    "Entertainment": ["netflix", "spotify", "cinema", "streaming"],
    "Health": ["pharmacy", "gym", "doctor"],
    "Shopping": ["amazon", "laptop", "mall"],
}


def guess_category(description: str) -> str:
    text = str(description).lower()
    for category, words in KEYWORDS.items():
        if any(w in text for w in words):
            return category
    return "Other"


def categorize(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing categories using keywords; tidy existing ones."""
    df = df.copy()
    df["category"] = df["category"].astype(object)  # empty column loads as float NaN
    missing = df["category"].isna() | (df["category"].astype(str).str.strip() == "")
    df.loc[missing, "category"] = df.loc[missing, "description"].apply(guess_category)
    df["category"] = df["category"].astype(str).str.strip().str.title()
    return df
