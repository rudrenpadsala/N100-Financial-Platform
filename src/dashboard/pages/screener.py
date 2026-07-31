import streamlit as st
import pandas as pd

from utils.db import (
    get_companies,
    get_ratios,
    get_sectors,
)


# -------------------------------------------------------
# Safe Helper
# -------------------------------------------------------
def safe_series(df, column, default=0):

    if column not in df.columns:
        return pd.Series([default] * len(df))

    return df[column].fillna(default)


# -------------------------------------------------------
# Screener Page
# -------------------------------------------------------
def show():

    st.title("📊 Stock Screener")

    # ---------------------------------------------------
    # Load Data
    # ---------------------------------------------------

    companies = get_companies()
    ratios = get_ratios()
    sectors = get_sectors()

    if ratios.empty:

        st.warning("Financial Ratio data not available.")

        st.stop()

    # ---------------------------------------------------
    # Merge Company Names
    # ---------------------------------------------------

    ratios = ratios.merge(

        companies[
            [
                "id",
                "company_name",
            ]
        ],

        left_on="company_id",

        right_on="id",

        how="left",

    )

    # ---------------------------------------------------
    # Merge Sector
    # ---------------------------------------------------

    ratios = ratios.merge(

        sectors[
            [
                "company_id",
                "broad_sector",
            ]
        ],

        on="company_id",

        how="left",

    )

    # ---------------------------------------------------
    # Latest Year Only
    # ---------------------------------------------------

    latest_year = ratios["year"].max()

    ratios = ratios[
        ratios["year"] == latest_year
    ].copy()

    # ---------------------------------------------------
    # Fill Missing Values
    # ---------------------------------------------------

    ratios["return_on_equity_pct"] = safe_series(
        ratios,
        "return_on_equity_pct",
    )

    ratios["debt_to_equity"] = safe_series(
        ratios,
        "debt_to_equity",
    )

    ratios["free_cash_flow_cr"] = safe_series(
        ratios,
        "free_cash_flow_cr",
    )

    ratios["revenue_cagr_5yr"] = safe_series(
        ratios,
        "revenue_cagr_5yr",
    )

    ratios["pat_cagr_5yr"] = safe_series(
        ratios,
        "pat_cagr_5yr",
    )

    ratios["operating_profit_margin_pct"] = safe_series(
        ratios,
        "operating_profit_margin_pct",
    )

    ratios["interest_coverage"] = safe_series(
        ratios,
        "interest_coverage",
    )

    ratios["composite_quality_score"] = safe_series(
        ratios,
        "composite_quality_score",
    )

        # ---------------------------------------------------
    # Sidebar Filters
    # ---------------------------------------------------

    st.sidebar.header("📌 Screener Filters")

    roe_min = st.sidebar.slider(
        "Minimum ROE (%)",
        0.0,
        50.0,
        10.0,
        0.5,
    )

    debt_max = st.sidebar.slider(
        "Maximum Debt / Equity",
        0.0,
        5.0,
        1.0,
        0.1,
    )

    fcf_min = st.sidebar.slider(
        "Minimum Free Cash Flow (Cr)",
        float(ratios["free_cash_flow_cr"].min()),
        float(ratios["free_cash_flow_cr"].max()),
        0.0,
    )

    revenue_min = st.sidebar.slider(
        "Minimum Revenue CAGR (%)",
        -20.0,
        50.0,
        5.0,
        0.5,
    )

    pat_min = st.sidebar.slider(
        "Minimum PAT CAGR (%)",
        -20.0,
        50.0,
        5.0,
        0.5,
    )

    opm_min = st.sidebar.slider(
        "Minimum OPM (%)",
        0.0,
        80.0,
        10.0,
        0.5,
    )

    st.sidebar.info(
        "⚠ P/E and P/B filters are unavailable because valuation data is not loaded."
    )

    dividend_min = st.sidebar.slider(
        "Minimum Dividend Payout (%)",
        0.0,
        100.0,
        0.0,
        1.0,
    )

    icr_min = st.sidebar.slider(
        "Minimum Interest Coverage",
        0.0,
        50.0,
        3.0,
        0.5,
    )

    # ---------------------------------------------------
    # Preset Buttons
    # ---------------------------------------------------

    st.subheader("🎯 Quick Presets")

    b1, b2, b3, b4, b5 = st.columns(5)

    preset = None

    if b1.button("Quality"):
        preset = "quality"

    if b2.button("Growth"):
        preset = "growth"

    if b3.button("Dividend"):
        preset = "dividend"

    if b4.button("Debt-Free"):
        preset = "debt"

    if b5.button("Turnaround"):
        preset = "turnaround"

    # ---------------------------------------------------
    # Apply Presets
    # ---------------------------------------------------

    if preset == "quality":

        roe_min = 20
        debt_max = 0.5
        revenue_min = 10
        pat_min = 10
        opm_min = 15
        icr_min = 5

    elif preset == "growth":

        roe_min = 15
        revenue_min = 15
        pat_min = 15

    elif preset == "dividend":

        dividend_min = 30

    elif preset == "debt":

        debt_max = 0.1

    elif preset == "turnaround":

        revenue_min = 5
        pat_min = 5
        fcf_min = 0

        # ---------------------------------------------------
    # Apply Filters
    # ---------------------------------------------------

    filtered = ratios.copy()

    filtered = filtered[
        filtered["return_on_equity_pct"] >= roe_min
    ]

    filtered = filtered[
        filtered["debt_to_equity"] <= debt_max
    ]

    filtered = filtered[
        filtered["free_cash_flow_cr"] >= fcf_min
    ]

    filtered = filtered[
        filtered["revenue_cagr_5yr"] >= revenue_min
    ]

    filtered = filtered[
        filtered["pat_cagr_5yr"] >= pat_min
    ]

    filtered = filtered[
        filtered["operating_profit_margin_pct"] >= opm_min
    ]

    filtered = filtered[
        filtered["dividend_payout_ratio_pct"] >= dividend_min
    ]

    filtered = filtered[
        filtered["interest_coverage"] >= icr_min
    ]

    # ---------------------------------------------------
    # Sort by Quality Score
    # ---------------------------------------------------

    filtered = filtered.sort_values(
        by="composite_quality_score",
        ascending=False,
    )

    # ---------------------------------------------------
    # Result Count
    # ---------------------------------------------------

    st.markdown("---")

    st.subheader("📈 Screening Results")

    st.success(
        f"✅ {len(filtered)} companies match your filters."
    )

    # ---------------------------------------------------
    # Display Columns
    # ---------------------------------------------------

    display_df = filtered[
        [
            "company_id",
            "company_name",
            "broad_sector",
            "return_on_equity_pct",
            "debt_to_equity",
            "free_cash_flow_cr",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "operating_profit_margin_pct",
            "interest_coverage",
            "dividend_payout_ratio_pct",
            "composite_quality_score",
        ]
    ].copy()

    display_df = display_df.rename(
        columns={
            "company_id": "Company ID",
            "company_name": "Company",
            "broad_sector": "Sector",
            "return_on_equity_pct": "ROE (%)",
            "debt_to_equity": "Debt/Equity",
            "free_cash_flow_cr": "FCF (Cr)",
            "revenue_cagr_5yr": "Revenue CAGR (%)",
            "pat_cagr_5yr": "PAT CAGR (%)",
            "operating_profit_margin_pct": "OPM (%)",
            "interest_coverage": "Interest Coverage",
            "dividend_payout_ratio_pct": "Dividend Payout (%)",
            "composite_quality_score": "Quality Score",
        }
    )

        # ---------------------------------------------------
    # Results Table
    # ---------------------------------------------------

    st.markdown("---")

    if display_df.empty:

        st.warning(
            "No companies match the selected filters."
        )

    else:

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

    # ---------------------------------------------------
    # Download CSV
    # ---------------------------------------------------

    if not display_df.empty:

        csv = display_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="📥 Download Results (CSV)",
            data=csv,
            file_name="screener_results.csv",
            mime="text/csv",
        )

    # ---------------------------------------------------
    # Quick Statistics
    # ---------------------------------------------------

    if not display_df.empty:

        st.markdown("---")

        st.subheader("📊 Filter Summary")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Companies",
            len(display_df)
        )

        c2.metric(
            "Average ROE",
            f"{display_df['ROE (%)'].mean():.2f}%"
        )

        c3.metric(
            "Average Revenue CAGR",
            f"{display_df['Revenue CAGR (%)'].mean():.2f}%"
        )

        c4.metric(
            "Average Quality Score",
            f"{display_df['Quality Score'].mean():.2f}"
        )

        # ---------------------------------------------------
    # Top 10 Quality Companies
    # ---------------------------------------------------

    if not display_df.empty:

        st.markdown("---")

        st.subheader("🏆 Top 10 Companies by Quality Score")

        top10 = (
            display_df
            .sort_values(
                "Quality Score",
                ascending=False,
            )
            .head(10)
        )

        st.dataframe(
            top10,
            use_container_width=True,
            hide_index=True,
        )

    # ---------------------------------------------------
    # Dataset Information
    # ---------------------------------------------------

    st.markdown("---")

    with st.expander("ℹ Dataset Information"):

        st.write(
            f"**Financial Year:** {latest_year}"
        )

        st.write(
            f"**Total Companies Loaded:** {len(ratios)}"
        )

        st.write(
            f"**Companies Matching Filters:** {len(display_df)}"
        )

        st.write(
            "**Database Tables Used:**"
        )

        st.markdown(
            """
- Companies
- Financial Ratios
- Sectors
            """
        )

        st.info(
            "P/E Ratio and P/B Ratio filters are currently disabled because valuation data has not been loaded into the database."
        )

    # ---------------------------------------------------
    # Footer
    # ---------------------------------------------------

    st.markdown("---")

    st.caption(
        "📊 N100 Financial Analytics Dashboard | Sprint 4 | Day 24 | Stock Screener"
    )