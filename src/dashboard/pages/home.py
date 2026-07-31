import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import (
    get_companies,
    get_ratios,
    get_sectors,
)


def show():

    st.title("🏠 Nifty 100 Analytics Dashboard")

    companies = get_companies()
    ratios = get_ratios()
    sectors = get_sectors()

    # -------------------------
    # Sidebar Year Filter
    # -------------------------

    years = sorted(ratios["year"].unique(), reverse=True)

    selected_year = st.sidebar.selectbox(
        "Select Year",
        years,
    )

    ratios = ratios[ratios["year"] == selected_year]

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

    st.subheader("Summary")

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

        st.subheader("Sector Breakdown")

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
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with right:

        st.subheader("Top 5 Quality Companies")

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

        st.dataframe(
            top5,
            use_container_width=True,
            hide_index=True,
        )