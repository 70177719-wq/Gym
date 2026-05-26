from __future__ import annotations

import pandas as pd


def filter_data(
    df: pd.DataFrame,
    regions: list[str] | None = None,
    countries: list[str] | None = None,
    year_range: tuple[int, int] | None = None,
) -> pd.DataFrame:
    filtered = df.copy()
    if regions:
        filtered = filtered[filtered["region"].isin(regions)]
    if countries:
        filtered = filtered[filtered["country"].isin(countries)]
    if year_range:
        start, end = year_range
        filtered = filtered[(filtered["year"] >= start) & (filtered["year"] <= end)]
    return filtered


def yearly_global(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("year", as_index=False)
        .agg(
            gym_memberships=("gym_memberships", "sum"),
            total_health_club_revenue_usd=("total_health_club_revenue_usd", "sum"),
            number_of_gyms=("number_of_gyms", "sum"),
            fitness_participation_pct=("fitness_participation_pct", "mean"),
            gym_penetration_pct=("gym_penetration_pct", "mean"),
            obesity_pct=("obesity_pct", "mean"),
            insufficient_activity_pct=("insufficient_activity_pct", "mean"),
            wellness_score=("wellness_score", "mean"),
            revenue_billion=("revenue_billion", "sum"),
            members_million=("members_million", "sum"),
        )
        .sort_values("year")
    )


def region_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("region", as_index=False)
        .agg(
            countries=("country", "nunique"),
            gym_memberships=("gym_memberships", "sum"),
            total_health_club_revenue_usd=("total_health_club_revenue_usd", "sum"),
            number_of_gyms=("number_of_gyms", "sum"),
            population_total=("population_total", "sum"),
            fitness_participation_pct=("fitness_participation_pct", "mean"),
            gym_penetration_pct=("gym_penetration_pct", "mean"),
            obesity_pct=("obesity_pct", "mean"),
            wellness_score=("wellness_score", "mean"),
            market_power_index=("market_power_index", "mean"),
            gdp_per_capita_usd=("gdp_per_capita_usd", "mean"),
        )
        .sort_values("market_power_index", ascending=False)
    )


def country_latest(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    latest_year = int(df["year"].max())
    return df[df["year"] == latest_year].sort_values("market_power_index", ascending=False).copy()


def top_n(df: pd.DataFrame, metric: str, n: int = 10) -> pd.DataFrame:
    if metric not in df:
        return df.head(0)
    return df.sort_values(metric, ascending=False).head(n).copy()


def correlation_frame(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    existing = [column for column in columns if column in df.columns]
    if len(existing) < 2:
        return pd.DataFrame()
    return df[existing].corr(numeric_only=True).round(3)
