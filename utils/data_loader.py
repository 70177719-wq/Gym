from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATHS = [
    BASE_DIR / "data" / "clean_gym_data.csv",
    BASE_DIR.parent / "clean_gym_data.csv",
    BASE_DIR.parent / "Bilaref2c2" / "clean_gym_data.csv",
]

NUMERIC_COLUMNS = [
    "year",
    "gym_memberships",
    "fitness_participation_rate",
    "total_health_club_revenue_usd",
    "number_of_gyms",
    "gym_penetration_rate",
    "urban_population_percentage",
    "obesity_rate",
    "gdp_per_capita_usd",
    "population_total",
    "average_membership_cost_usd",
    "insufficient_physical_activity_pct",
]


def _resolve_data_path() -> Path:
    for path in DATA_PATHS:
        if path.exists():
            return path
    checked = "\n".join(str(path) for path in DATA_PATHS)
    raise FileNotFoundError(
        "clean_gym_data.csv was not found. Place it at project/data/clean_gym_data.csv "
        f"or the repository root.\nChecked:\n{checked}"
    )


def _percent_series(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce").fillna(0)
    return pd.Series(np.where(numeric.abs() <= 1.5, numeric * 100, numeric), index=series.index)


@st.cache_data(show_spinner="Synchronizing global fitness intelligence...")
def load_data() -> pd.DataFrame:
    path = _resolve_data_path()
    df = pd.read_csv(path)
    df.columns = [column.strip().lower() for column in df.columns]

    required = {"country", "year", "region"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")

    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df["country"] = df["country"].fillna("Unknown").astype(str).str.strip()
    df["region"] = df["region"].fillna("Unclassified").astype(str).str.strip()
    df["year"] = df["year"].fillna(df["year"].median()).astype(int)

    numeric_cols = df.select_dtypes(include=["number"]).columns
    df[numeric_cols] = df[numeric_cols].replace([np.inf, -np.inf], np.nan)
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median(numeric_only=True))

    df["fitness_participation_pct"] = _percent_series(df["fitness_participation_rate"])
    df["gym_penetration_pct"] = _percent_series(df["gym_penetration_rate"])
    df["urban_population_pct"] = _percent_series(df["urban_population_percentage"])
    df["obesity_pct"] = _percent_series(df["obesity_rate"])
    df["insufficient_activity_pct"] = _percent_series(df["insufficient_physical_activity_pct"])
    df["members_million"] = df["gym_memberships"] / 1_000_000
    df["revenue_billion"] = df["total_health_club_revenue_usd"] / 1_000_000_000
    df["population_million"] = df["population_total"] / 1_000_000
    df["gyms_per_million_people"] = (df["number_of_gyms"] / df["population_million"].replace(0, np.nan)).fillna(0)
    df["revenue_per_member"] = (
        df["total_health_club_revenue_usd"] / df["gym_memberships"].replace(0, np.nan)
    ).fillna(0)
    df["wellness_score"] = (
        df["fitness_participation_pct"] * 0.38
        + df["gym_penetration_pct"] * 0.22
        + (100 - df["obesity_pct"]).clip(lower=0) * 0.22
        + (100 - df["insufficient_activity_pct"]).clip(lower=0) * 0.18
    ).clip(lower=0, upper=100)
    df["market_power_index"] = (
        df["revenue_billion"].rank(pct=True) * 35
        + df["members_million"].rank(pct=True) * 30
        + df["gym_penetration_pct"].rank(pct=True) * 20
        + df["gdp_per_capita_usd"].rank(pct=True) * 15
    ).round(2)

    return df.sort_values(["year", "region", "country"]).reset_index(drop=True)


def latest_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    latest_year = int(df["year"].max())
    return df[df["year"] == latest_year].copy()
