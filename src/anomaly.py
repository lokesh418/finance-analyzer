"""Detect unusually large expenses using per-category z-scores."""
import pandas as pd
from .analysis import expenses


def detect_anomalies(df: pd.DataFrame, z_threshold: float = 2.5,
                     min_group: int = 5) -> pd.DataFrame:
    exp = expenses(df)
    g = exp.groupby("category")["spend"]
    exp["count"] = g.transform("size")
    mean, std = g.transform("mean"), g.transform("std")
    exp["z_score"] = ((exp["spend"] - mean) / std.where(std > 0)).round(2)
    out = exp[(exp["count"] >= min_group) & (exp["z_score"] > z_threshold)]
    return (out[["date", "description", "category", "spend", "z_score"]]
            .sort_values("z_score", ascending=False).reset_index(drop=True))
