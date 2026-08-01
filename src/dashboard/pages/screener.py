import streamlit as st
import pandas as pd
from io import BytesIO

from utils.db import (
    get_companies,
    get_ratios,
    get_sectors,
)

# ==========================================================
# Styling
# ==========================================================

def inject_css():
    st.markdown(
        """
<style>

@keyframes fadeInUp{
    from{opacity:0;transform:translateY(14px);}
    to{opacity:1;transform:translateY(0);}
}

.main .block-container{
    animation:fadeInUp .6s ease-out;
    padding-top:2rem;
}

h1{
    background:linear-gradient(90deg,#6C63FF,#FF6B9D,#FFB86C);
    background-size:200% auto;
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    animation:shimmer 6s linear infinite;
    font-weight:800!important;
}

@keyframes shimmer{
    0%{background-position:0%;}
    100%{background-position:200%;}
}

h2,h3{
    border-left:4px solid #6C63FF;
    padding-left:.6rem;
    font-weight:700!important;
}

div[data-testid="stMetric"]{
    background:linear-gradient(
        135deg,
        rgba(108,99,255,.08),
        rgba(255,107,157,.08)
    );
    border:1px solid rgba(108,99,255,.25);
    border-radius:16px;
    padding:1rem;
    transition:.25s;
}

div[data-testid="stMetric"]:hover{
    transform:translateY(-4px);
    box-shadow:0 8px 18px rgba(108,99,255,.25);
}

div[data-testid="stDataFrame"],
div[data-testid="stPlotlyChart"]{
    border-radius:14px;
    overflow:hidden;
}

section[data-testid="stSidebar"]{
    background:linear-gradient(
        180deg,
        rgba(108,99,255,.05),
        rgba(255,107,157,.02)
    );
}

</style>
""",
        unsafe_allow_html=True,
    )


def divider():
    st.markdown(
        "<hr style='margin-top:1rem;margin-bottom:1rem;'>",
        unsafe_allow_html=True,
    )


# ==========================================================
# Helper Functions
# ==========================================================

def safe_series(df, column, default=0):
    if column not in df.columns:
        return pd.Series([default] * len(df))

    return df[column].fillna(default)


def rating(score):
    if score >= 80:
        return "⭐⭐⭐⭐⭐"

    elif score >= 60:
        return "⭐⭐⭐⭐"

    elif score >= 40:
        return "⭐⭐⭐"

    elif score >= 20:
        return "⭐⭐"

    return "⭐"


def to_excel(df):

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            sheet_name="Screener",
            index=False,
        )

    return output.getvalue()

# ==========================================================
# Screener Page
# ==========================================================

def show():

    inject_css()

    st.title("📊 Stock Screener")

    # ------------------------------------------------------
    # Load Data
    # ------------------------------------------------------

    companies = get_companies()
    ratios = get_ratios()
    sectors = get_sectors()

    if ratios.empty:
        st.warning("Financial ratio data not available.")
        st.stop()

    # ------------------------------------------------------
    # Merge Company Names
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Merge Sector Information
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Fill Missing Values
    # ------------------------------------------------------

    numeric_columns = [

        "return_on_equity_pct",

        "debt_to_equity",

        "free_cash_flow_cr",

        "revenue_cagr_5yr",

        "pat_cagr_5yr",

        "operating_profit_margin_pct",

        "interest_coverage",

        "composite_quality_score",

        "dividend_payout_ratio_pct",

    ]

    for col in numeric_columns:
        ratios[col] = safe_series(ratios, col)

    # ------------------------------------------------------
    # Sidebar Filters
    # ------------------------------------------------------

    st.sidebar.header("📌 Filters")

    # ---------------- Year ----------------

    ratios["calendar_year"] = (
        ratios["year"]
        .astype(str)
        .str[-4:]
        .astype(int)
    )

    available_years = sorted(
        ratios["calendar_year"].unique(),
        reverse=True,
    )

    selected_year = st.sidebar.selectbox(
        "Financial Year",
        available_years,
    )

    ratios = ratios[
        ratios["calendar_year"] == selected_year
    ]

    # ---------------- Sector ----------------

    sector_list = ["All"] + sorted(
        ratios["broad_sector"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_sector = st.sidebar.selectbox(
        "Sector",
        sector_list,
    )

    if selected_sector != "All":

        ratios = ratios[
            ratios["broad_sector"] == selected_sector
        ]

    # ---------------- Company Search ----------------

    company_search = st.sidebar.text_input(
        "🔍 Search Company"
    )

    if company_search:

        ratios = ratios[
            ratios["company_name"]
            .str.contains(
                company_search,
                case=False,
                na=False,
            )
        ]

    # ---------------- Reset ----------------

    if st.sidebar.button("🔄 Reset Filters"):
        st.rerun()

        # ======================================================
    # Dynamic Slider Ranges
    # ======================================================

    st.sidebar.header("📊 Financial Filters")

    roe_min = st.sidebar.slider(
        "Minimum ROE (%)",
        float(ratios["return_on_equity_pct"].min()),
        float(ratios["return_on_equity_pct"].max()),
        10.0,
    )

    debt_max = st.sidebar.slider(
        "Maximum Debt / Equity",
        float(ratios["debt_to_equity"].min()),
        float(ratios["debt_to_equity"].max()),
        1.0,
    )

    fcf_min = st.sidebar.slider(
        "Minimum Free Cash Flow (Cr)",
        float(ratios["free_cash_flow_cr"].min()),
        float(ratios["free_cash_flow_cr"].max()),
        0.0,
    )

    revenue_min = st.sidebar.slider(
        "Minimum Revenue CAGR (%)",
        float(ratios["revenue_cagr_5yr"].min()),
        float(ratios["revenue_cagr_5yr"].max()),
        5.0,
    )

    pat_min = st.sidebar.slider(
        "Minimum PAT CAGR (%)",
        float(ratios["pat_cagr_5yr"].min()),
        float(ratios["pat_cagr_5yr"].max()),
        5.0,
    )

    opm_min = st.sidebar.slider(
        "Minimum OPM (%)",
        float(ratios["operating_profit_margin_pct"].min()),
        float(ratios["operating_profit_margin_pct"].max()),
        10.0,
    )

    dividend_min = st.sidebar.slider(
        "Minimum Dividend Payout (%)",
        float(ratios["dividend_payout_ratio_pct"].min()),
        float(ratios["dividend_payout_ratio_pct"].max()),
        0.0,
    )

    icr_min = st.sidebar.slider(
        "Minimum Interest Coverage",
        float(ratios["interest_coverage"].min()),
        float(ratios["interest_coverage"].max()),
        3.0,
    )

    # ======================================================
    # Sorting
    # ======================================================

    st.sidebar.header("⬇ Sorting")

    sort_column = st.sidebar.selectbox(
        "Sort By",
        [
            "Quality Score",
            "ROE",
            "Revenue CAGR",
            "PAT CAGR",
            "Debt/Equity",
            "Free Cash Flow",
        ],
    )

    ascending = st.sidebar.checkbox(
        "Ascending",
        False,
    )

    sort_map = {
        "Quality Score": "composite_quality_score",
        "ROE": "return_on_equity_pct",
        "Revenue CAGR": "revenue_cagr_5yr",
        "PAT CAGR": "pat_cagr_5yr",
        "Debt/Equity": "debt_to_equity",
        "Free Cash Flow": "free_cash_flow_cr",
    }

    # ======================================================
    # Quick Presets
    # ======================================================

    divider()

    st.subheader("🎯 Quick Presets")

    c1, c2, c3, c4, c5 = st.columns(5)

    preset = None

    if c1.button("Quality"):
        preset = "quality"

    if c2.button("Growth"):
        preset = "growth"

    if c3.button("Dividend"):
        preset = "dividend"

    if c4.button("Debt-Free"):
        preset = "debt"

    if c5.button("Turnaround"):
        preset = "turnaround"

    if preset == "quality":

        roe_min = 20
        debt_max = 0.50
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

        debt_max = 0.10

    elif preset == "turnaround":

        revenue_min = 5
        pat_min = 5
        fcf_min = 0

        # ======================================================
    # Apply Filters
    # ======================================================

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
        filtered["interest_coverage"] >= icr_min
    ]

    filtered = filtered[
        filtered["dividend_payout_ratio_pct"] >= dividend_min
    ]

    # ======================================================
    # Sorting
    # ======================================================

    filtered = filtered.sort_values(
        by=sort_map[sort_column],
        ascending=ascending,
    )

    # ======================================================
    # Quality Rating
    # ======================================================

    filtered["Rating"] = filtered[
        "composite_quality_score"
    ].apply(rating)

    # ======================================================
    # Result Count
    # ======================================================

    divider()

    st.subheader("📈 Screening Results")

    st.success(
        f"✅ {len(filtered)} companies match your filters."
    )

    st.info(
        f"Financial Year : {selected_year}   |   Sector : {selected_sector}"
    )

    # ======================================================
    # Sector Summary
    # ======================================================

    if not filtered.empty:

        st.subheader("🏢 Sector Summary")

        sector_summary = (
            filtered
            .groupby("broad_sector")
            .size()
            .reset_index(name="Companies")
            .sort_values(
                "Companies",
                ascending=False,
            )
        )

        st.dataframe(
            sector_summary,
            use_container_width=True,
            hide_index=True,
        )

    # ======================================================
    # Display Data
    # ======================================================

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
            "Rating",
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

        # ======================================================
    # Results Table
    # ======================================================

    divider()

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

    # ======================================================
    # Download Buttons
    # ======================================================

    if not display_df.empty:

        divider()

        csv = display_df.to_csv(
            index=False
        ).encode("utf-8")

        excel = to_excel(display_df)

        d1, d2 = st.columns(2)

        with d1:

            st.download_button(
                "📥 Download CSV",
                csv,
                "screener_results.csv",
                "text/csv",
            )

        with d2:

            st.download_button(
                "📗 Download Excel",
                excel,
                "screener_results.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    # ======================================================
    # Summary Statistics
    # ======================================================

    if not display_df.empty:

        divider()

        st.subheader("📊 Filter Summary")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Companies",
            len(display_df),
        )

        c2.metric(
            "Average ROE",
            f"{display_df['ROE (%)'].mean():.2f}%",
        )

        c3.metric(
            "Average Revenue CAGR",
            f"{display_df['Revenue CAGR (%)'].mean():.2f}%",
        )

        c4.metric(
            "Average Quality Score",
            f"{display_df['Quality Score'].mean():.2f}",
        )

    # ======================================================
    # Top 10 Companies
    # ======================================================

    if not display_df.empty:

        divider()

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

    # ======================================================
    # Dataset Information
    # ======================================================

    divider()

    with st.expander("ℹ Dataset Information"):

        st.write(
            f"**Financial Year:** {selected_year}"
        )

        st.write(
            f"**Selected Sector:** {selected_sector}"
        )

        st.write(
            f"**Companies Loaded:** {len(ratios)}"
        )

        st.write(
            f"**Companies Matching Filters:** {len(display_df)}"
        )

        st.markdown(
            """
### Database Tables Used

- Companies
- Financial Ratios
- Sectors

### Current Limitations

- P/E Ratio filter unavailable
- P/B Ratio filter unavailable
- Valuation table will be added in Sprint 5
            """
        )

    # ======================================================
    # Footer
    # ======================================================

    divider()

    st.caption(
        "📊 N100 Financial Analytics Dashboard | Sprint 4 | Day 24 | Stock Screener"
    )

    

    