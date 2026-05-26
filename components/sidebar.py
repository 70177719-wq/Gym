from __future__ import annotations

import streamlit as st


PAGES = [
    "Executive Overview",
    "Global Fitness Analytics",
    "Revenue Intelligence",
    "Country Comparison",
    "Health & Obesity Analytics",
    "Membership Trends",
    "AI Insights Center",
    "Predictive Analytics",
    "Regional Intelligence",
    "Settings & Themes",
]

ICONS = [
    "01",
    "02",
    "03",
    "04",
    "05",
    "06",
    "07",
    "08",
    "09",
    "10",
]


def render_sidebar(df) -> dict:
    years = sorted(df["year"].dropna().astype(int).unique().tolist())
    regions = sorted(df["region"].dropna().unique().tolist())
    countries = sorted(df["country"].dropna().unique().tolist())

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-logo">
                <div class="logo-orb">AI</div>
                <div>
                    <h2>GYM NEXUS</h2>
                    <p>Global Fitness Intelligence</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav_labels = [f"{icon}  {page}" for icon, page in zip(ICONS, PAGES)]
        selected_label = st.radio("Navigation", nav_labels, label_visibility="collapsed")
        page = PAGES[nav_labels.index(selected_label)]

        st.markdown("<div class='sidebar-section'>Control Matrix</div>", unsafe_allow_html=True)
        year_range = st.slider("Year Range", min_value=min(years), max_value=max(years), value=(min(years), max(years)))
        selected_regions = st.multiselect("Regions", options=regions, default=regions)
        selected_countries = st.multiselect("Countries", options=countries, default=[])
        top_n = st.slider("Leaderboard Size", 5, 25, 10)
        theme_intensity = st.select_slider("Glow Intensity", options=["Subtle", "Neon", "Hyperdrive"], value="Neon")

        st.markdown(
            """
            <div class="sidebar-footer">
                <span class="pulse-dot"></span>
                Streamlit Cloud Safe
            </div>
            """,
            unsafe_allow_html=True,
        )

    return {
        "page": page,
        "year_range": year_range,
        "regions": selected_regions,
        "countries": selected_countries,
        "top_n": top_n,
        "theme_intensity": theme_intensity,
    }
