from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT / "data" / "sample"


DATE_COLUMNS = {
    "reservations": ["date_booked", "check_in", "check_out"],
    "web_analytics": ["date"],
    "seo_queries": ["date"],
    "reviews": ["date"],
    "issues": ["date"],
}


def load_table(name: str) -> tuple[pd.DataFrame, str]:
    path = SAMPLE_DIR / f"{name}.csv"
    source = "sample"
    if not path.exists():
        return pd.DataFrame(), "missing"

    df = pd.read_csv(path)
    for column in DATE_COLUMNS.get(name, []):
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")
    return df, source


def filter_by_date(df: pd.DataFrame, column: str, start, end) -> pd.DataFrame:
    if df.empty or column not in df.columns:
        return df
    return df[(df[column] >= pd.Timestamp(start)) & (df[column] <= pd.Timestamp(end))]


def data_freshness(df: pd.DataFrame, date_column: str) -> str:
    if df.empty or date_column not in df.columns:
        return "No data"
    latest = df[date_column].max()
    if pd.isna(latest):
        return "No valid dates"
    return latest.strftime("%Y-%m-%d")
