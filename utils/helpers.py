from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]


def load_css() -> None:
    css_path = BASE_DIR / "styles" / "main.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def format_compact(value: float | int | None, currency: bool = False) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    sign = "$" if currency else ""
    value = float(value)
    absolute = abs(value)
    if absolute >= 1_000_000_000_000:
        return f"{sign}{value / 1_000_000_000_000:.2f}T"
    if absolute >= 1_000_000_000:
        return f"{sign}{value / 1_000_000_000:.2f}B"
    if absolute >= 1_000_000:
        return f"{sign}{value / 1_000_000:.2f}M"
    if absolute >= 1_000:
        return f"{sign}{value / 1_000:.1f}K"
    return f"{sign}{value:,.0f}"


def format_percent(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{float(value):.1f}%"


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator in (0, None) or pd.isna(denominator):
        return 0.0
    return float(numerator) / float(denominator)


def trend_delta(df: pd.DataFrame, value_col: str, year_col: str = "year") -> float:
    if df.empty or value_col not in df:
        return 0.0
    yearly = df.groupby(year_col, as_index=False)[value_col].sum().sort_values(year_col)
    if len(yearly) < 2:
        return 0.0
    previous = yearly[value_col].iloc[-2]
    current = yearly[value_col].iloc[-1]
    return safe_divide(current - previous, previous) * 100


def weighted_average(df: pd.DataFrame, value_col: str, weight_col: str = "population_total") -> float:
    if df.empty or value_col not in df:
        return 0.0
    values = df[value_col].fillna(0)
    if weight_col not in df or df[weight_col].fillna(0).sum() <= 0:
        return float(values.mean())
    weights = df[weight_col].fillna(0)
    return float(np.average(values, weights=weights))


def clean_multiselect(values: Iterable[str] | None, all_values: list[str]) -> list[str]:
    if not values:
        return all_values
    selected = [value for value in values if value in all_values]
    return selected or all_values
