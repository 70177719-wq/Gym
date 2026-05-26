from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


CYAN = "#00f5ff"
BLUE = "#2f80ff"
PURPLE = "#9b5cff"
GREEN = "#34f5a1"
PINK = "#ff4fd8"
GRID = "rgba(0,245,255,0.14)"
PAPER = "rgba(0,0,0,0)"
PLOT = "rgba(3,8,20,0.35)"


def apply_layout(fig: go.Figure, height: int = 420, title: str | None = None) -> go.Figure:
    fig.update_layout(
        title=title,
        height=height,
        template="plotly_dark",
        paper_bgcolor=PAPER,
        plot_bgcolor=PLOT,
        font=dict(color="#d7f9ff", family="Inter, Segoe UI, sans-serif"),
        margin=dict(l=20, r=20, t=55 if title else 25, b=25),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    return fig


def line_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str = "", height: int = 420) -> go.Figure:
    fig = px.line(df, x=x, y=y, color=color, markers=True, color_discrete_sequence=[CYAN, PURPLE, GREEN, BLUE, PINK])
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    return apply_layout(fig, height=height, title=title)


def area_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str = "", height: int = 420) -> go.Figure:
    fig = px.area(df, x=x, y=y, color=color, color_discrete_sequence=[BLUE, CYAN, PURPLE, GREEN, PINK])
    fig.update_traces(opacity=0.68, line=dict(width=2))
    return apply_layout(fig, height=height, title=title)


def bar_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str = "", height: int = 420) -> go.Figure:
    fig = px.bar(df, x=x, y=y, color=color or x, color_continuous_scale=["#101827", CYAN, GREEN])
    fig.update_traces(marker_line_color="rgba(255,255,255,0.24)", marker_line_width=1)
    return apply_layout(fig, height=height, title=title)


def scatter_bubble(
    df: pd.DataFrame,
    x: str,
    y: str,
    size: str,
    color: str,
    hover_name: str = "country",
    title: str = "",
    height: int = 470,
) -> go.Figure:
    fig = px.scatter(
        df,
        x=x,
        y=y,
        size=size,
        color=color,
        hover_name=hover_name,
        size_max=52,
        color_continuous_scale=["#2d1b69", BLUE, CYAN, GREEN],
    )
    fig.update_traces(marker=dict(line=dict(width=1, color="rgba(255,255,255,0.35)"), opacity=0.82))
    return apply_layout(fig, height=height, title=title)


def heatmap(corr: pd.DataFrame, title: str = "Correlation Matrix", height: int = 430) -> go.Figure:
    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.index,
            colorscale=[[0, "#311354"], [0.5, "#101827"], [1, CYAN]],
            zmin=-1,
            zmax=1,
            text=corr.values,
            texttemplate="%{text:.2f}",
            hovertemplate="%{y} vs %{x}: %{z:.2f}<extra></extra>",
        )
    )
    return apply_layout(fig, height=height, title=title)


def choropleth(df: pd.DataFrame, color: str, title: str = "", height: int = 500) -> go.Figure:
    fig = px.choropleth(
        df,
        locations="country",
        locationmode="country names",
        color=color,
        hover_name="country",
        hover_data=["region", "fitness_participation_pct", "gym_penetration_pct", "wellness_score"],
        color_continuous_scale=["#1b1038", "#124d8f", CYAN, GREEN],
        projection="natural earth",
    )
    fig.update_geos(bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=True, coastlinecolor="rgba(0,245,255,0.2)")
    return apply_layout(fig, height=height, title=title)


def radar_chart(row: pd.Series, title: str = "Country Fitness Radar") -> go.Figure:
    categories = ["Fitness Participation", "Gym Penetration", "Wellness Score", "GDP Index", "Market Power"]
    values = [
        float(row.get("fitness_participation_pct", 0)),
        float(row.get("gym_penetration_pct", 0)),
        float(row.get("wellness_score", 0)),
        min(float(row.get("gdp_per_capita_usd", 0)) / 1_000, 100),
        float(row.get("market_power_index", 0)),
    ]
    values.append(values[0])
    categories.append(categories[0])
    fig = go.Figure(
        data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            line=dict(color=CYAN, width=3),
            fillcolor="rgba(0,245,255,0.22)",
            name=str(row.get("country", "Selected Country")),
        )
    )
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, max(100, np.nanmax(values))])))
    return apply_layout(fig, height=430, title=title)


def gauge(value: float, title: str, suffix: str = "") -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=float(value),
            number={"suffix": suffix, "font": {"color": "#d7f9ff"}},
            title={"text": title, "font": {"color": "#d7f9ff"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#d7f9ff"},
                "bar": {"color": CYAN},
                "bgcolor": "rgba(255,255,255,0.04)",
                "borderwidth": 1,
                "bordercolor": "rgba(0,245,255,0.35)",
                "steps": [
                    {"range": [0, 35], "color": "rgba(255,79,216,0.25)"},
                    {"range": [35, 70], "color": "rgba(47,128,255,0.22)"},
                    {"range": [70, 100], "color": "rgba(52,245,161,0.25)"},
                ],
            },
        )
    )
    return apply_layout(fig, height=300)
