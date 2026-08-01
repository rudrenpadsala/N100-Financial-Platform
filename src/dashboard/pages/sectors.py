import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import (
    get_companies,
    get_ratios,
    get_sectors,
)
from utils.theme import page_header

# Fix 4: market cap is optional — import defensively so the page
# still works if utils/db.py doesn't actually expose this function.
try:
    from utils.db import get_market_cap
    HAS_MARKET_CAP = True
except ImportError:
    HAS_MARKET_CAP = False


# =========================================================
# Helper Functions
# =========================================================

def divider():
    st.markdown("<hr/>", unsafe_allow_html=True)


def safe_series(df, column, default=0):

    if column not in df.columns:
        return pd.Series([default] * len(df))

    return df[column].fillna(default)


def safe_float(value):

    try:

        if pd.isna(value):
            return 0.0

        return float(value)

    except Exception:

        return 0.0

# =========================================================
# Sector Analysis
# =========================================================

def show():

    page_header(
        "🏭",
        "Sector Analysis",
        "Compare sectors across profitability, leverage and growth.",
    )

    # -----------------------------------------------------
    # Load Data
    # -----------------------------------------------------

    companies = get_companies()
    ratios = get_ratios()
    sectors = get_sectors()

    if (
        companies.empty
        or ratios.empty
        or sectors.empty
    ):

        st.warning(
            "Sector data not available."
        )

        st.stop()

    # -----------------------------------------------------
    # Rename Company ID
    # -----------------------------------------------------

    companies = companies.rename(
        columns={
            "id": "company_id"
        }
    )

    # -----------------------------------------------------
    # Merge Company Names
    # -----------------------------------------------------

    df = ratios.merge(

        companies[
            [
                "company_id",
                "company_name",
            ]
        ],

        on="company_id",

        how="left",

    )

    # -----------------------------------------------------
    # Merge Sector Data
    # -----------------------------------------------------

    df = df.merge(

        sectors,

        on="company_id",

        how="left",

    )

    # -----------------------------------------------------
    # Fill Missing Values
    # -----------------------------------------------------

    df["return_on_equity_pct"] = safe_series(
        df,
        "return_on_equity_pct",
    )

    df["revenue_cagr_5yr"] = safe_series(
        df,
        "revenue_cagr_5yr",
    )

    df["free_cash_flow_cr"] = safe_series(
        df,
        "free_cash_flow_cr",
    )

    df["composite_quality_score"] = safe_series(
        df,
        "composite_quality_score",
    )

    df["index_weight_pct"] = safe_series(
        df,
        "index_weight_pct",
    )

    # -----------------------------------------------------
    # FIX 1: Keep latest record PER COMPANY, not just the
    # single latest year across the whole table.
    #
    # The old code did:
    #     latest_year = df["year"].max()
    #     df = df[df["year"] == latest_year]
    # Since only 1 company (SIEMENS) had a Sep 2024 row while
    # the other 91 were on Mar 2024, this silently dropped
    # everyone else. Grouping per company_id and taking each
    # company's own latest year fixes that.
    # -----------------------------------------------------

    df = (
        df
        .sort_values("year")
        .groupby("company_id", as_index=False)
        .last()
    )

    latest_year = "Latest Available"

    # -----------------------------------------------------
    # FIX 4 (data prep): try to bring in market cap for the
    # bubble chart. Falls back to quality score if the table
    # or column isn't actually available.
    # -----------------------------------------------------

    bubble_size_col = "composite_quality_score"
    bubble_size_label = "Quality Score"

    if HAS_MARKET_CAP:
        try:
            market = get_market_cap()

            if (
                not market.empty
                and "company_id" in market.columns
                and "market_cap_crore" in market.columns
            ):
                df = df.merge(
                    market[["company_id", "market_cap_crore"]],
                    on="company_id",
                    how="left",
                )

                if df["market_cap_crore"].notna().any():
                    bubble_size_col = "market_cap_crore"
                    bubble_size_label = "Market Cap (Cr)"
        except Exception:
            # Market cap unavailable/broken — silently keep the
            # quality-score fallback rather than crashing the page.
            pass

    # -----------------------------------------------------
    # Sidebar (FIX 2: richer filters)
    # -----------------------------------------------------

    st.sidebar.header("🔍 Filters")

    sector_list = sorted(
        df["broad_sector"].dropna().unique().tolist()
    )

    selected_sector = st.sidebar.selectbox(
        "Sector",
        ["All"] + sector_list,
    )

    subsector_list = sorted(
        df["sub_sector"].dropna().unique().tolist()
    )

    selected_subsector = st.sidebar.selectbox(
        "Sub Sector",
        ["All"] + subsector_list,
    )

    search_company = st.sidebar.text_input(
        "Search Company"
    )

    roe = st.sidebar.slider(
        "Minimum ROE (%)",
        0,
        50,
        10,
    )

    growth = st.sidebar.slider(
        "Minimum Revenue CAGR (%)",
        -20,
        50,
        0,
    )

    quality = st.sidebar.slider(
        "Minimum Quality Score",
        0,
        100,
        0,
    )

    # -----------------------------------------------------
    # FIX 3: Apply filters
    # -----------------------------------------------------

    sector_df = df.copy()

    if selected_sector != "All":
        sector_df = sector_df[
            sector_df["broad_sector"] == selected_sector
        ]

    if selected_subsector != "All":
        sector_df = sector_df[
            sector_df["sub_sector"] == selected_subsector
        ]

    if search_company:
        sector_df = sector_df[
            sector_df["company_name"]
            .str.contains(
                search_company,
                case=False,
                na=False,
            )
        ]

    sector_df = sector_df[
        sector_df["return_on_equity_pct"] >= roe
    ]

    sector_df = sector_df[
        sector_df["revenue_cagr_5yr"] >= growth
    ]

    sector_df = sector_df[
        sector_df["composite_quality_score"] >= quality
    ]

    if sector_df.empty:

        st.warning(
            "No companies match the selected filters."
        )

        st.stop()

    # -----------------------------------------------------
    # KPI Cards
    # -----------------------------------------------------

    header_label = (
        selected_sector if selected_sector != "All" else "All Sectors"
    )

    st.subheader(header_label)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Companies",
        len(sector_df),
    )

    c2.metric(
        "Average ROE",
        f"{sector_df['return_on_equity_pct'].mean():.2f}%"
    )

    c3.metric(
        "Average Revenue CAGR",
        f"{sector_df['revenue_cagr_5yr'].mean():.2f}%"
    )

    c4.metric(
        "Average Quality Score",
        f"{sector_df['composite_quality_score'].mean():.2f}"
    )

    divider()

    # -----------------------------------------------------
    # Bubble Chart (FIX 4: market cap sizing, with fallback)
    # -----------------------------------------------------

    st.subheader("📈 Sector Bubble Chart")

    st.caption(
        f"X = Revenue CAGR | Y = ROE | Bubble Size = {bubble_size_label} | Colour = Sub Sector"
    )

    bubble_df = sector_df.copy()

    bubble_df["return_on_equity_pct"] = (
        bubble_df["return_on_equity_pct"]
        .fillna(0)
    )

    bubble_df["revenue_cagr_5yr"] = (
        bubble_df["revenue_cagr_5yr"]
        .fillna(0)
    )

    bubble_df[bubble_size_col] = (
        bubble_df[bubble_size_col]
        .fillna(0 if bubble_size_col == "market_cap_crore" else 10)
    )

    # size values must be non-negative for plotly
    bubble_df[bubble_size_col] = bubble_df[bubble_size_col].clip(lower=0)

    bubble_df["sub_sector"] = (
        bubble_df["sub_sector"]
        .fillna("Unknown")
    )

    bubble_df["company_name"] = (
        bubble_df["company_name"]
        .fillna("Unknown")
    )

    fig = px.scatter(

        bubble_df,

        x="revenue_cagr_5yr",

        y="return_on_equity_pct",

        size=bubble_size_col,

        color="sub_sector",

        hover_name="company_name",

        hover_data={

            "revenue_cagr_5yr": ":.2f",

            "return_on_equity_pct": ":.2f",

            bubble_size_col: ":.2f",

            "sub_sector": True,

        },

        size_max=60,

    )

    fig.update_traces(

        marker=dict(

            opacity=0.85,

            line=dict(
                width=1,
                color="white",
            ),

        )

    )

    fig.update_layout(

        height=650,

        template="plotly_white",

        xaxis_title="Revenue CAGR (%)",

        yaxis_title="ROE (%)",

        legend_title="Sub Sector",

        hovermode="closest",

        margin=dict(

            l=20,

            r=20,

            t=40,

            b=20,

        ),

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

    divider()

    # -----------------------------------------------------
    # Sector Median KPI Chart
    # -----------------------------------------------------

    st.subheader("📊 Sector Median KPIs")

    median_df = pd.DataFrame(

        {

            "Metric": [

                "ROE",

                "Revenue CAGR",

                "FCF",

                "Quality Score",

            ],

            "Value": [

                sector_df["return_on_equity_pct"].median(),

                sector_df["revenue_cagr_5yr"].median(),

                sector_df["free_cash_flow_cr"].median(),

                sector_df["composite_quality_score"].median(),

            ],

        }

    )

    bar = px.bar(

        median_df,

        x="Metric",

        y="Value",

        color="Metric",

        text="Value",

    )

    bar.update_traces(

        texttemplate="%{text:.2f}",

        textposition="outside",

    )

    bar.update_layout(

        height=500,

        template="plotly_white",

        showlegend=False,

        yaxis_title="Median Value",

        xaxis_title="",

    )

    st.plotly_chart(

        bar,

        use_container_width=True,

    )

    divider()

    # -----------------------------------------------------
    # Top Companies
    # -----------------------------------------------------

    st.subheader("🏆 Top Companies in Sector")

    top_companies = (

        sector_df

        .sort_values(

            "composite_quality_score",

            ascending=False,

        )

        [

            [

                "company_name",

                "sub_sector",

                "return_on_equity_pct",

                "revenue_cagr_5yr",

                "free_cash_flow_cr",

                "composite_quality_score",

            ]

        ]

        .copy()

    )

    top_companies.columns = [

        "Company",

        "Sub Sector",

        "ROE (%)",

        "Revenue CAGR (%)",

        "FCF (Cr)",

        "Quality Score",

    ]

    st.dataframe(

        top_companies,

        use_container_width=True,

        hide_index=True,

    )

    divider()

    # -----------------------------------------------------
    # Download CSV
    # -----------------------------------------------------

    st.subheader("📥 Export Data")

    csv = top_companies.to_csv(
        index=False
    ).encode("utf-8")

    export_name = (
        selected_sector.lower().replace(" ", "_")
        if selected_sector != "All"
        else "all_sectors"
    )

    st.download_button(
        label="Download Sector Analysis (CSV)",
        data=csv,
        file_name=f"{export_name}_sector_analysis.csv",
        mime="text/csv",
    )

    divider()

    # -----------------------------------------------------
    # Sector Summary
    # -----------------------------------------------------

    st.subheader("📈 Sector Summary")

    s1, s2, s3 = st.columns(3)

    s1.metric(
        "Highest ROE",
        f"{sector_df['return_on_equity_pct'].max():.2f}%"
    )

    s2.metric(
        "Highest Revenue CAGR",
        f"{sector_df['revenue_cagr_5yr'].max():.2f}%"
    )

    s3.metric(
        "Highest Quality Score",
        f"{sector_df['composite_quality_score'].max():.2f}"
    )

    divider()

    # -----------------------------------------------------
    # Dataset Information
    # -----------------------------------------------------

    with st.expander("ℹ Dataset Information"):

        st.write(
            f"**Financial Year:** {latest_year} (per-company latest)"
        )

        st.write(
            f"**Selected Sector:** {header_label}"
        )

        st.write(
            f"**Companies Shown:** {len(sector_df)}"
        )

        st.write(
            f"**Total Companies:** {len(df)}"
        )

        market_cap_note = (
            "Market Capitalization data is available and is used for bubble size."
            if bubble_size_col == "market_cap_crore"
            else "Market Capitalization data is not available in the current database, "
                 "so Composite Quality Score is used as the bubble size."
        )

        st.markdown(
            f"""
### Bubble Chart

- **X Axis:** Revenue CAGR (5 Years)
- **Y Axis:** Return on Equity (ROE)
- **Bubble Size:** {bubble_size_label}
- **Bubble Colour:** Sub Sector

### Data Sources

- Companies
- Financial Ratios
- Sectors

> Note: {market_cap_note}
            """
        )

    divider()

    # -----------------------------------------------------
    # Footer
    # -----------------------------------------------------

    st.caption(
        "📊 N100 Financial Analytics Dashboard | Sector Analysis"
    )