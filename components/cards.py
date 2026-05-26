from __future__ import annotations

import streamlit as st


def hero(title: str, subtitle: str, eyebrow: str = "AI Fitness Intelligence") -> None:
    st.markdown(
        f"""
        <section class="hero-panel">
            <div class="hero-eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
            <div class="hero-gridline"></div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, delta: str = "", icon: str = "◆", accent: str = "cyan") -> None:
    delta_html = f"<span class='metric-delta'>{delta}</span>" if delta else ""
    st.markdown(
        f"""
        <div class="glass-card metric-card accent-{accent}">
            <div class="metric-topline">
                <span class="metric-icon">{icon}</span>
                {delta_html}
            </div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(title: str, body: str, score: float | int = 0, accent: str = "cyan") -> None:
    st.markdown(
        f"""
        <div class="glass-card insight-card accent-{accent}">
            <div class="insight-header">
                <span class="pulse-dot"></span>
                <span>{title}</span>
                <strong>{float(score):.0f}%</strong>
            </div>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_label(label: str, caption: str = "") -> None:
    caption_html = f"<p>{caption}</p>" if caption else ""
    st.markdown(
        f"""
        <div class="section-label">
            <span></span>
            <div>
                <h3>{label}</h3>
                {caption_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def ai_terminal(lines: list[str]) -> None:
    rendered_lines = "".join(f"<div><span>&gt;</span> {line}</div>" for line in lines)
    st.markdown(
        f"""
        <div class="ai-terminal">
            <div class="terminal-bar">
                <span></span><span></span><span></span>
                <strong>NEURAL_INSIGHTS_ENGINE.py</strong>
            </div>
            <div class="terminal-body">{rendered_lines}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
