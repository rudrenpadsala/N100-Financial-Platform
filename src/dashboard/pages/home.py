import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import (
    get_companies,
    get_ratios,
    get_sectors,
)


# =========================================================
# Styling (CSS + animations)
# =========================================================

def inject_css():
    st.markdown(
        """
        <style>

        /* ---------- Global fade-in for the whole page ---------- */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(14px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        .main .block-container {
            animation: fadeInUp 0.6s ease-out;
            padding-top: 2rem;
        }

        /* ---------- Title ---------- */
        h1 {
            background: linear-gradient(90deg, #6C63FF, #FF6B9D, #FFB86C);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: shimmer 6s linear infinite;
            font-weight: 800 !important;
        }

        @keyframes shimmer {
            0%   { background-position: 0% center; }
            100% { background-position: 200% center; }
        }

        /* ---------- Subheaders ---------- */
        h2, h3 {
            font-weight: 700 !important;
            border-left: 4px solid #6C63FF;
            padding-left: 0.6rem;
            animation: fadeInUp 0.6s ease-out;
        }

        /* ---------- KPI metric cards ---------- */
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(108,99,255,0.08), rgba(255,107,157,0.08));
            border: 1px solid rgba(108,99,255,0.25);
            border-radius: 16px;
            padding: 1rem 1rem 0.6rem 1rem;
            box-shadow: 0 4px 14px rgba(0,0,0,0.06);
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
            animation: fadeInUp 0.7s ease-out;
        }

        div[data-testid="stMetric"]:hover {
            transform: translateY(-6px) scale(1.02);
            box-shadow: 0 10px 24px rgba(108,99,255,0.25);
            border-color: #6C63FF;
        }

        div[data-testid="stMetricLabel"] {
            font-weight: 600;
            opacity: 0.75;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.6rem !important;
            font-weight: 800 !important;
        }

        /* Stagger the 6 KPI cards slightly for a nicer entrance */
        div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] { animation-delay: 0.05s; }
        div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] { animation-delay: 0.10s; }
        div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] { animation-delay: 0.15s; }

        /* ---------- Divider ---------- */
        hr {
            margin-top: 1.2rem;
            margin-bottom: 1.2rem;
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #6C63FF, transparent);
            animation: fadeInUp 0.8s ease-out;
        }

        /* ---------- Charts & dataframe containers ---------- */
        div[data-testid="stPlotlyChart"], div[data-testid="stDataFrame"] {
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
            transition: box-shadow 0.25s ease, transform 0.25s ease;
            animation: fadeInUp 0.8s ease-out;
        }

        div[data-testid="stPlotlyChart"]:hover, div[data-testid="stDataFrame"]:hover {
            box-shadow: 0 10px 26px rgba(0,0,0,0.12);
            transform: translateY(-3px);
        }

        /* ---------- Sidebar ---------- */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(108,99,255,0.06), rgba(255,107,157,0.03));
        }

        section[data-testid="stSidebar"] .stSelectbox label {
            font-weight: 700;
            color: #6C63FF;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def section_header(text: str):
    """Small helper so subheaders animate in with a slight stagger."""
    st.markdown(f"### {text}")


def show():

    inject_css()

    st.title("🏠 Nifty 100 Analytics Dashboard")

    companies = get_companies()
    ratios = get_ratios()
    sectors = get_sectors()

    # -------------------------
    # Sidebar Year Filter
    # -------------------------

    ratios["calendar_year"] = (
    ratios["year"]
    .str[-4:]
    .astype(int)
)

    years = sorted(
        ratios["calendar_year"].unique(),
        reverse=True,
    )

    selected_year = st.sidebar.selectbox(
        "Select Year",
        years,
    )

    ratios = ratios[
        ratios["calendar_year"] == selected_year
    ]

    # -------------------------
    # Merge Data
    # -------------------------

    companies = companies.rename(columns={"id": "company_id"})

    df = ratios.merge(
        companies,
        on="company_id",
        how="left",
    )

    df = df.merge(
        sectors,
        on="company_id",
        how="left",
    )

    # -------------------------
    # KPI Cards
    # -------------------------

    section_header("Summary")

    c1, c2, c3 = st.columns(3)
    c4, c5, c6 = st.columns(3)

    c1.metric(
        "Average ROE",
        f"{df['return_on_equity_pct'].mean():.2f}%"
    )

    c2.metric(
        "Median P/E",
        "Coming Day 26"
    )

    c3.metric(
        "Median D/E",
        f"{df['debt_to_equity'].median():.2f}"
    )

    c4.metric(
        "Total Companies",
        len(companies)
    )

    c5.metric(
        "Median Revenue CAGR",
        f"{df['revenue_cagr_5yr'].median():.2f}%"
    )

    c6.metric(
        "Debt-Free Companies",
        int((df["debt_to_equity"] <= 0.10).sum())
    )

    st.divider()

    # -------------------------
    # Charts
    # -------------------------

    left, right = st.columns(2)

    with left:

        section_header("Sector Breakdown")

        sector_df = (
            df.groupby("broad_sector")
            .size()
            .reset_index(name="Companies")
        )

        fig = px.pie(
            sector_df,
            names="broad_sector",
            values="Companies",
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.Sunsetdark,
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            pull=[0.03] * len(sector_df),
            marker=dict(line=dict(color="#ffffff", width=2)),
        )

        fig.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
            transition=dict(duration=500, easing="cubic-in-out"),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with right:

        section_header("Top 5 Quality Companies")

        top5 = (
            df.sort_values(
                "composite_quality_score",
                ascending=False,
            )
            .head(5)[
                [
                    "company_name",
                    "return_on_equity_pct",
                    "debt_to_equity",
                    "composite_quality_score",
                ]
            ]
        )

        try:
            styled_top5 = top5.style.background_gradient(
                subset=["composite_quality_score"],
                cmap="Purples",
            )
        except Exception:
            # matplotlib not installed, or gradient styling failed -
            # fall back to a plain (unstyled) table instead of crashing.
            styled_top5 = top5

        st.dataframe(
            styled_top5,
            use_container_width=True,
            hide_index=True,
        )