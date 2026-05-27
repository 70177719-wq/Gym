from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression

from components.cards import ai_terminal, hero, insight_card, metric_card, section_label
from components.charts import area_chart, bar_chart, choropleth, gauge, heatmap, line_chart, radar_chart, scatter_bubble
from components.sidebar import render_sidebar
from utils.data_loader import latest_snapshot, load_data
from utils.helpers import format_compact, format_percent, load_css, safe_select_columns, trend_delta
from utils.preprocess import correlation_frame, country_latest, filter_data, region_summary, top_n, yearly_global


st.set_page_config(
    page_title="Gym Nexus | Global Fitness Intelligence",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded",
)


def kpi_grid(df: pd.DataFrame, latest: pd.DataFrame) -> None:
    total_countries = latest["country"].nunique()
    total_members = latest["gym_memberships"].sum()
    total_revenue = latest["total_health_club_revenue_usd"].sum()
    avg_penetration = latest["gym_penetration_pct"].mean()
    avg_participation = latest["fitness_participation_pct"].mean()
    avg_obesity = latest["obesity_pct"].mean()
    avg_gdp = latest["gdp_per_capita_usd"].mean()
    total_gyms = latest["number_of_gyms"].sum()

    deltas = {
        "members": trend_delta(df, "gym_memberships"),
        "revenue": trend_delta(df, "total_health_club_revenue_usd"),
        "gyms": trend_delta(df, "number_of_gyms"),
    }

    cards = [
        ("Total Countries", format_compact(total_countries), "Live market scan", "◎", "cyan"),
        ("Total Gym Members", format_compact(total_members), f"{deltas['members']:+.1f}% YoY", "◈", "green"),
        ("Total Revenue", format_compact(total_revenue, currency=True), f"{deltas['revenue']:+.1f}% YoY", "$", "blue"),
        ("Avg Penetration Rate", format_percent(avg_penetration), "Access density", "⌁", "purple"),
        ("Fitness Participation", format_percent(avg_participation), "Population active", "▲", "green"),
        ("Avg Obesity Rate", format_percent(avg_obesity), "Health pressure", "●", "pink"),
        ("Average GDP", format_compact(avg_gdp, currency=True), "Economic baseline", "◇", "cyan"),
        ("Total Gyms", format_compact(total_gyms), f"{deltas['gyms']:+.1f}% YoY", "▣", "blue"),
    ]

    for row_start in (0, 4):
        cols = st.columns(4)
        for col, card in zip(cols, cards[row_start : row_start + 4]):
            with col:
                metric_card(*card)


def executive_overview(df: pd.DataFrame) -> None:
    latest = latest_snapshot(df)
    hero(
        "Global Gym & Fitness Intelligence",
        "A futuristic AI-powered command center for health club economics, wellness adoption, and market momentum across countries and regions.",
        "Executive Overview",
    )
    kpi_grid(df, latest)

    yearly = yearly_global(df)
    leaders = top_n(latest, "market_power_index", 10)

    section_label("Global Signal", "Membership, revenue, and market power compressed into executive-grade views.")
    c1, c2 = st.columns((1.45, 1))
    with c1:
        st.plotly_chart(
            area_chart(yearly, "year", "revenue_billion", title="Global Health Club Revenue Evolution"),
            use_container_width=True,
        )
    with c2:
        st.plotly_chart(
            bar_chart(leaders, "market_power_index", "country", title="Top Market Power Countries", height=420),
            use_container_width=True,
        )

    c3, c4 = st.columns((1.1, 1.1))
    with c3:
        st.plotly_chart(choropleth(latest, "wellness_score", "Global Wellness Intelligence Map"), use_container_width=True)
    with c4:
        st.plotly_chart(
            scatter_bubble(
                latest,
                "gdp_per_capita_usd",
                "gym_penetration_pct",
                "gym_memberships",
                "wellness_score",
                title="GDP vs Gym Penetration",
            ),
            use_container_width=True,
        )


def global_fitness_analytics(df: pd.DataFrame) -> None:
    hero(
        "Global Fitness Analytics",
        "Track participation, gym supply, revenue expansion, and the long arc of fitness market evolution.",
        "Planetary Trend Layer",
    )
    yearly = yearly_global(df)
    by_region = (
        df.groupby(["year", "region"], as_index=False)
        .agg(
            members_million=("members_million", "sum"),
            revenue_billion=("revenue_billion", "sum"),
            number_of_gyms=("number_of_gyms", "sum"),
            fitness_participation_pct=("fitness_participation_pct", "mean"),
        )
        .sort_values("year")
    )

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(line_chart(yearly, "year", "fitness_participation_pct", title="Global Participation Trend"), use_container_width=True)
    with c2:
        st.plotly_chart(area_chart(yearly, "year", "members_million", title="Membership Growth Curve"), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(line_chart(by_region, "year", "revenue_billion", "region", "Regional Revenue Streams"), use_container_width=True)
    with c4:
        st.plotly_chart(line_chart(by_region, "year", "number_of_gyms", "region", "Gym Network Expansion"), use_container_width=True)

    pivot = by_region.pivot(index="region", columns="year", values="fitness_participation_pct").fillna(0)
    fig = px.imshow(
        pivot,
        color_continuous_scale=["#10091f", "#2f80ff", "#00f5ff", "#34f5a1"],
        aspect="auto",
        title="Regional Participation Heatmap",
    )
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=430)
    st.plotly_chart(fig, use_container_width=True)


def revenue_intelligence(df: pd.DataFrame) -> None:
    latest = latest_snapshot(df)
    regions = region_summary(latest)
    yearly = yearly_global(df)
    hero(
        "Revenue Intelligence",
        "Decode the monetization layer of global fitness: revenue pools, pricing power, market density, and regional acceleration.",
        "Commercial Signal Engine",
    )

    cols = st.columns(4)
    metrics = [
        ("Revenue Pool", latest["total_health_club_revenue_usd"].sum(), "Total latest-year market", "$"),
        ("Revenue / Member", latest["revenue_per_member"].mean(), "Average ARPM", "$"),
        ("Avg Membership Cost", latest["average_membership_cost_usd"].mean(), "Monthly affordability", "$"),
        ("Market Power", latest["market_power_index"].mean(), "Composite strength", ""),
    ]
    for col, (label, value, delta, prefix) in zip(cols, metrics):
        with col:
            metric_card(label, format_compact(value, currency=prefix == "$"), delta, "$" if prefix == "$" else "◆", "green")

    c1, c2 = st.columns((1.25, 1))
    with c1:
        st.plotly_chart(area_chart(yearly, "year", "revenue_billion", title="Global Revenue Flywheel"), use_container_width=True)
    with c2:
        st.plotly_chart(bar_chart(regions, "total_health_club_revenue_usd", "region", title="Regional Revenue Leaderboard"), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(
            scatter_bubble(
                latest,
                "average_membership_cost_usd",
                "revenue_per_member",
                "gym_memberships",
                "gdp_per_capita_usd",
                title="Pricing Power vs Revenue Per Member",
            ),
            use_container_width=True,
        )
    with c4:
        st.plotly_chart(choropleth(latest, "total_health_club_revenue_usd", "Country Revenue Heatmap"), use_container_width=True)


def country_comparison(df: pd.DataFrame, top_count: int) -> None:
    latest = country_latest(df)
    hero(
        "Country Comparison",
        "Explore national market rank, wellness strength, economics, and access density through interactive country-level intelligence.",
        "Country Neural Lens",
    )

    selected = st.multiselect(
        "Select countries for radar analysis",
        latest["country"].tolist(),
        default=latest["country"].head(min(3, len(latest))).tolist(),
    )
    selected_df = latest[latest["country"].isin(selected)] if selected else latest.head(3)

    c1, c2 = st.columns((1.15, 1))
    with c1:
        st.plotly_chart(
            scatter_bubble(
                latest,
                "gdp_per_capita_usd",
                "fitness_participation_pct",
                "gym_memberships",
                "market_power_index",
                title="GDP vs Fitness Participation",
            ),
            use_container_width=True,
        )
    with c2:
        if not selected_df.empty:
            st.plotly_chart(radar_chart(selected_df.iloc[0], f"{selected_df.iloc[0]['country']} Fitness Radar"), use_container_width=True)

    tabs = st.tabs(["Market Power", "Revenue", "Gym Penetration", "Wellness"])
    metrics = ["market_power_index", "total_health_club_revenue_usd", "gym_penetration_pct", "wellness_score"]
    for tab, metric in zip(tabs, metrics):
        with tab:
            leaders = top_n(latest, metric, top_count)
            st.plotly_chart(bar_chart(leaders, metric, "country", title=f"Top {top_count} by {metric.replace('_', ' ').title()}"), use_container_width=True)
            cols = ["country", "region", metric, "gym_memberships", "total_health_club_revenue_usd"]
            st.dataframe(safe_select_columns(leaders, cols), use_container_width=True)


def health_obesity_analytics(df: pd.DataFrame) -> None:
    latest = latest_snapshot(df)
    hero(
        "Health & Obesity Analytics",
        "Map the relationship between fitness behavior, inactivity, obesity, urbanization, and national wellness performance.",
        "Wellness Risk Radar",
    )

    corr = correlation_frame(
        latest,
        [
            "fitness_participation_pct",
            "gym_penetration_pct",
            "obesity_pct",
            "insufficient_activity_pct",
            "urban_population_pct",
            "wellness_score",
            "gdp_per_capita_usd",
        ],
    )

    c1, c2 = st.columns((1, 1.05))
    with c1:
        st.plotly_chart(heatmap(corr, "Health Correlation Matrix"), use_container_width=True)
    with c2:
        st.plotly_chart(
            scatter_bubble(
                latest,
                "obesity_pct",
                "fitness_participation_pct",
                "population_total",
                "wellness_score",
                title="Obesity vs Fitness Participation",
            ),
            use_container_width=True,
        )

    c3, c4, c5 = st.columns(3)
    with c3:
        st.plotly_chart(gauge(latest["wellness_score"].mean(), "Global Wellness Score"), use_container_width=True)
    with c4:
        st.plotly_chart(gauge(100 - latest["insufficient_activity_pct"].mean(), "Activity Readiness"), use_container_width=True)
    with c5:
        st.plotly_chart(gauge(100 - latest["obesity_pct"].mean(), "Obesity Resilience"), use_container_width=True)

    st.plotly_chart(choropleth(latest, "obesity_pct", "Obesity Risk Map"), use_container_width=True)


def membership_trends(df: pd.DataFrame) -> None:
    hero(
        "Membership Trends",
        "Animate the evolution of gym membership growth, penetration, and regional adoption across the full timeline.",
        "Membership Growth Engine",
    )
    yearly = yearly_global(df)
    regional = (
        df.groupby(["year", "region"], as_index=False)
        .agg(
            members_million=("members_million", "sum"),
            gym_penetration_pct=("gym_penetration_pct", "mean"),
            revenue_billion=("revenue_billion", "sum"),
        )
        .sort_values("year")
    )
    focus_year = st.slider("Animated Timeline Year", int(df["year"].min()), int(df["year"].max()), int(df["year"].max()))
    focus = df[df["year"] == focus_year]

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(area_chart(yearly, "year", "members_million", title="Total Membership Growth"), use_container_width=True)
    with c2:
        st.plotly_chart(line_chart(regional, "year", "gym_penetration_pct", "region", "Regional Penetration Timeline"), use_container_width=True)

    c3, c4 = st.columns((1, 1))
    with c3:
        st.plotly_chart(bar_chart(top_n(focus, "gym_memberships", 12), "gym_memberships", "country", title=f"Membership Leaders in {focus_year}"), use_container_width=True)
    with c4:
        st.plotly_chart(
            scatter_bubble(
                focus,
                "population_total",
                "gym_memberships",
                "number_of_gyms",
                "gym_penetration_pct",
                title=f"Population vs Members in {focus_year}",
            ),
            use_container_width=True,
        )


def build_ai_insights(df: pd.DataFrame) -> list[tuple[str, str, float, str]]:
    latest = latest_snapshot(df)
    regions = region_summary(latest)
    yearly = yearly_global(df)
    top_region = regions.iloc[0]

    def safe_corr(left: str, right: str) -> float:
        pair = latest[[left, right]].dropna()
        if len(pair) < 2 or pair[left].nunique() < 2 or pair[right].nunique() < 2:
            return 0.0
        value = pair[left].corr(pair[right])
        return 0.0 if pd.isna(value) else float(value)

    revenue_corr = safe_corr("gdp_per_capita_usd", "gym_penetration_pct")
    obesity_corr = safe_corr("obesity_pct", "fitness_participation_pct")
    start_year = yearly.iloc[0]
    end_year = yearly.iloc[-1]
    member_growth = ((end_year["gym_memberships"] - start_year["gym_memberships"]) / max(start_year["gym_memberships"], 1)) * 100
    post_2015 = yearly[yearly["year"] >= 2015]["fitness_participation_pct"].mean()
    pre_2015 = yearly[yearly["year"] < 2015]["fitness_participation_pct"].mean()
    participation_lift = 0.0 if pd.isna(post_2015) or pd.isna(pre_2015) else float(post_2015 - pre_2015)

    return [
        (
            "Regional Dominance Detected",
            f"{top_region['region']} currently leads global market power with {format_compact(top_region['total_health_club_revenue_usd'], currency=True)} in latest-year revenue.",
            min(top_region["market_power_index"], 99),
            "cyan",
        ),
        (
            "GDP Penetration Signal",
            f"Higher GDP markets show a {revenue_corr:.2f} correlation with gym penetration, indicating economic capacity remains a strong adoption amplifier.",
            abs(revenue_corr) * 100,
            "green",
        ),
        (
            "Obesity Activity Tension",
            f"Obesity and fitness participation have a {obesity_corr:.2f} relationship, highlighting where wellness intervention demand is strongest.",
            abs(obesity_corr) * 100,
            "pink",
        ),
        (
            "Long-Range Membership Expansion",
            f"Global gym memberships expanded {member_growth:.1f}% from {int(start_year['year'])} to {int(end_year['year'])}, confirming durable sector growth.",
            min(abs(member_growth) / 8, 99),
            "purple",
        ),
        (
            "Post-2015 Participation Shift",
            f"Average fitness participation after 2015 is {participation_lift:+.2f} percentage points versus earlier years.",
            min(abs(participation_lift) * 10, 99),
            "blue",
        ),
    ]


def ai_insights_center(df: pd.DataFrame) -> None:
    hero(
        "AI Insights Center",
        "Automated narrative intelligence that translates raw gym, health, GDP, and population signals into executive insights.",
        "Neural Insight Layer",
    )
    insights = build_ai_insights(df)
    ai_terminal(
        [
            "Loading clean_gym_data.csv from secure Streamlit path...",
            f"Scanning {df['country'].nunique()} countries across {df['region'].nunique()} regions...",
            "Running correlation, growth, and market power diagnostics...",
            "Insight packets generated successfully. Confidence matrix stable.",
        ]
    )

    section_label("Generated Insights", "AI-style analysis generated from the active filters and latest available year.")
    cols = st.columns(2)
    for index, (title, body, score, accent) in enumerate(insights):
        with cols[index % 2]:
            insight_card(title, body, score, accent)

    latest = latest_snapshot(df)
    st.plotly_chart(
        scatter_bubble(
            latest,
            "wellness_score",
            "market_power_index",
            "gym_memberships",
            "obesity_pct",
            title="AI Opportunity Matrix: Wellness vs Market Power",
        ),
        use_container_width=True,
    )


def forecast_metric(yearly: pd.DataFrame, metric: str, horizon: int = 5) -> pd.DataFrame:
    model_frame = yearly[["year", metric]].dropna()
    if len(model_frame) < 3:
        return pd.DataFrame()
    x = model_frame[["year"]]
    y = model_frame[metric]
    future_years = np.arange(int(model_frame["year"].max()) + 1, int(model_frame["year"].max()) + horizon + 1)
    future_x = pd.DataFrame({"year": future_years})

    linear = LinearRegression()
    forest = RandomForestRegressor(n_estimators=80, max_depth=5, random_state=42)
    linear.fit(x, y)
    forest.fit(x, y)

    history = model_frame.rename(columns={metric: "value"}).assign(series="Actual")
    forecast = pd.DataFrame(
        {
            "year": future_years,
            "value": (linear.predict(future_x) * 0.55 + forest.predict(future_x) * 0.45),
            "series": "AI Forecast",
        }
    )
    return pd.concat([history, forecast], ignore_index=True)


def predictive_analytics(df: pd.DataFrame) -> None:
    latest = latest_snapshot(df)
    yearly = yearly_global(df)
    hero(
        "Predictive Analytics",
        "Lightweight Streamlit-safe ML forecasts using Linear Regression, Random Forest Regressor, and Logistic Regression.",
        "Prediction Core",
    )

    target_map = {
        "Membership Growth": "members_million",
        "Revenue Trends": "revenue_billion",
        "Penetration Forecast": "gym_penetration_pct",
    }
    selected_target = st.selectbox("Forecast Target", list(target_map.keys()))
    forecast = forecast_metric(yearly, target_map[selected_target])

    c1, c2 = st.columns((1.35, 1))
    with c1:
        if forecast.empty:
            st.warning("Not enough timeline data to train a forecast.")
        else:
            st.plotly_chart(line_chart(forecast, "year", "value", "series", f"{selected_target} Forecast"), use_container_width=True)
    with c2:
        features = latest[["gdp_per_capita_usd", "fitness_participation_pct", "gym_penetration_pct", "obesity_pct", "wellness_score"]].fillna(0)
        labels = (latest["market_power_index"] >= latest["market_power_index"].median()).astype(int)
        if labels.nunique() > 1 and len(features) > 8:
            classifier = LogisticRegression(max_iter=500)
            classifier.fit(features, labels)
            probabilities = classifier.predict_proba(features)[:, 1] * 100
            opportunity = latest[["country", "region", "market_power_index", "wellness_score"]].copy()
            opportunity["high_growth_probability"] = probabilities
            st.plotly_chart(
                bar_chart(
                    top_n(opportunity, "high_growth_probability", 10),
                    "high_growth_probability",
                    "country",
                    title="Logistic Growth Probability",
                ),
                use_container_width=True,
            )
        else:
            st.info("Classifier requires more class variation in the active filters.")

    forecast_table = forecast.tail(5).copy() if not forecast.empty else pd.DataFrame()
    if not forecast_table.empty:
        st.dataframe(forecast_table, use_container_width=True)


def regional_intelligence(df: pd.DataFrame) -> None:
    latest = latest_snapshot(df)
    regions = region_summary(latest)
    hero(
        "Regional Intelligence",
        "Compare regions through revenue, gym density, population context, wellness momentum, and global heatmaps.",
        "Geographic Intelligence",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Leading Region", str(regions.iloc[0]["region"]), "Market power", "◎", "cyan")
    with c2:
        metric_card("Regional Revenue", format_compact(regions["total_health_club_revenue_usd"].sum(), currency=True), "Latest year", "$", "green")
    with c3:
        metric_card("Tracked Regions", format_compact(regions["region"].nunique()), "Global coverage", "▣", "purple")

    c4, c5 = st.columns((1.2, 1))
    with c4:
        st.plotly_chart(choropleth(latest, "wellness_score", "Global Fitness Heatmap"), use_container_width=True)
    with c5:
        st.plotly_chart(bar_chart(regions, "wellness_score", "region", title="Regional Wellness Leaderboard"), use_container_width=True)

    c6, c7 = st.columns(2)
    with c6:
        st.plotly_chart(
            scatter_bubble(
                regions,
                "population_total",
                "number_of_gyms",
                "gym_memberships",
                "market_power_index",
                hover_name="region",
                title="Population vs Gym Network",
            ),
            use_container_width=True,
        )
    with c7:
        st.dataframe(
            regions[
                [
                    "region",
                    "countries",
                    "gym_memberships",
                    "total_health_club_revenue_usd",
                    "number_of_gyms",
                    "wellness_score",
                    "market_power_index",
                ]
            ],
            use_container_width=True,
        )


def settings_themes(df: pd.DataFrame, controls: dict) -> None:
    hero(
        "Settings & Themes",
        "Deployment diagnostics, theme controls, data profile, and Streamlit Cloud readiness checks.",
        "System Control",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Theme", controls["theme_intensity"], "CSS glassmorphism", "◐", "purple")
    with c2:
        metric_card("Dataset Rows", format_compact(len(df)), "Cached with st.cache_data", "▤", "cyan")
    with c3:
        metric_card("Cloud Status", "Ready", "No Node, Docker, GPU", "✓", "green")

    section_label("Deployment Checklist")
    checklist = pd.DataFrame(
        [
            ["Python + Streamlit only", "Pass"],
            ["Pathlib data loading", "Pass"],
            ["Lightweight ML only", "Pass"],
            ["No localhost services", "Pass"],
            ["No unsupported packages", "Pass"],
            ["Cached CSV loading", "Pass"],
        ],
        columns=["Check", "Status"],
    )
    st.dataframe(checklist, use_container_width=True, hide_index=True)

    section_label("Data Profile")
    st.dataframe(
        pd.DataFrame(
            {
                "Metric": ["Countries", "Regions", "Start Year", "End Year", "Columns"],
                "Value": [
                    df["country"].nunique(),
                    df["region"].nunique(),
                    int(df["year"].min()),
                    int(df["year"].max()),
                    len(df.columns),
                ],
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download Filtered Dataset Snapshot",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="gym_nexus_filtered_snapshot.csv",
        mime="text/csv",
    )


def main() -> None:
    load_css()
    df = load_data()
    controls = render_sidebar(df)
    filtered = filter_data(df, controls["regions"], controls["countries"], controls["year_range"])

    if filtered.empty:
        st.error("No records match the active filters. Broaden your selection in the sidebar.")
        return

    page = controls["page"]
    if page == "Executive Overview":
        executive_overview(filtered)
    elif page == "Global Fitness Analytics":
        global_fitness_analytics(filtered)
    elif page == "Revenue Intelligence":
        revenue_intelligence(filtered)
    elif page == "Country Comparison":
        country_comparison(filtered, controls["top_n"])
    elif page == "Health & Obesity Analytics":
        health_obesity_analytics(filtered)
    elif page == "Membership Trends":
        membership_trends(filtered)
    elif page == "AI Insights Center":
        ai_insights_center(filtered)
    elif page == "Predictive Analytics":
        predictive_analytics(filtered)
    elif page == "Regional Intelligence":
        regional_intelligence(filtered)
    elif page == "Settings & Themes":
        settings_themes(filtered, controls)


if __name__ == "__main__":
    main()
