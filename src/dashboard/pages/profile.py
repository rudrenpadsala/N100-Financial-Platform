import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from utils.db import (
    get_companies,
    get_ratios,
    get_pl,
    get_bs,
    get_cf,
    get_sectors,
)


# -------------------------------------------------------
# Safe Helper
# -------------------------------------------------------
def safe_value(value, default=0):
    """Return default when value is None or NaN."""
    if value is None:
        return default

    if pd.isna(value):
        return default

    return value


# -------------------------------------------------------
# Company Profile Page
# -------------------------------------------------------
def show():

    st.title("🏢 Company Profile")

    # ---------------------------------------------------
    # Load Companies
    # ---------------------------------------------------
    companies = get_companies()

    if companies.empty:
        st.error("Company database not found.")
        st.stop()

    company_names = sorted(
        companies["company_name"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_company = st.selectbox(
        "🔍 Search Company",
        company_names,
    )

    company = companies[
        companies["company_name"] == selected_company
    ]

    if company.empty:
        st.warning(
            "Ticker not found — please try another."
        )
        st.stop()

    company = company.iloc[0]

    company_id = company["id"]

    # ---------------------------------------------------
    # Load Database Tables
    # ---------------------------------------------------
    ratios = get_ratios(company_id)
    pl = get_pl(company_id)
    bs = get_bs(company_id)
    cf = get_cf(company_id)
    sectors = get_sectors()

    sector = sectors[
        sectors["company_id"] == company_id
    ]

    # ---------------------------------------------------
    # Validate Required Data
    # ---------------------------------------------------
    if ratios.empty:
        st.warning(
            "Financial Ratio data not available."
        )
        st.stop()

    if pl.empty:
        st.warning(
            "Profit & Loss data not available."
        )
        st.stop()

    latest = ratios.sort_values(
        "year"
    ).iloc[-1]

    # ---------------------------------------------------
    # Safe Variables
    # ---------------------------------------------------
    roe = safe_value(
        latest.get("return_on_equity_pct")
    )

    roce = safe_value(
        company.get("roce_percentage")
    )

    npm = safe_value(
        latest.get("net_profit_margin_pct")
    )

    debt = safe_value(
        latest.get("debt_to_equity")
    )

    revenue_cagr = safe_value(
        latest.get("revenue_cagr_5yr")
    )

    pat_cagr = safe_value(
        latest.get("pat_cagr_5yr")
    )

    eps_cagr = safe_value(
        latest.get("eps_cagr_5yr")
    )

    interest = safe_value(
        latest.get("interest_coverage")
    )

    fcf = safe_value(
        latest.get("free_cash_flow_cr")
    )

    quality = safe_value(
        latest.get("composite_quality_score")
    )


        # ==========================================================
    # Company Information
    # ==========================================================

    st.markdown("---")

    info_col, sector_col = st.columns([2, 1])

    with info_col:

        st.subheader(company["company_name"])

        ticker = company.get("chart_link")

        if pd.notna(ticker):
            st.write(f"**NSE Ticker:** {ticker}")

        about = company.get("about_company")

        if pd.notna(about):
            st.write(about)

        website = company.get("website")

        if pd.notna(website):
            st.write(f"🌐 **Website:** {website}")

        face_value = safe_value(company.get("face_value"))
        book_value = safe_value(company.get("book_value"))

        st.write(f"💰 **Face Value:** ₹{face_value}")

        st.write(f"📚 **Book Value:** ₹{book_value}")

    with sector_col:

        st.subheader("Sector Information")

        if not sector.empty:

            sector_row = sector.iloc[0]

            st.write(
                f"**Sector:** {sector_row['broad_sector']}"
            )

            st.write(
                f"**Sub Sector:** {sector_row['sub_sector']}"
            )

            index_weight = safe_value(
                sector_row.get("index_weight_pct")
            )

            st.write(
                f"**Index Weight:** {index_weight:.2f}%"
            )

            market_cap = sector_row.get(
                "market_cap_category"
            )

            if pd.notna(market_cap):
                st.write(
                    f"**Market Cap:** {market_cap}"
                )

        else:

            st.info(
                "Sector information not available."
            )

    # ==========================================================
    # KPI Cards
    # ==========================================================

    st.markdown("---")

    st.subheader("Key Financial Metrics")

    row1 = st.columns(3)
    row2 = st.columns(3)

    row1[0].metric(
        "ROE",
        f"{roe:.2f}%"
    )

    row1[1].metric(
        "ROCE",
        f"{roce:.2f}%"
    )

    row1[2].metric(
        "Net Profit Margin",
        f"{npm:.2f}%"
    )

    row2[0].metric(
        "Debt / Equity",
        f"{debt:.2f}"
    )

    row2[1].metric(
        "Revenue CAGR (5Y)",
        f"{revenue_cagr:.2f}%"
    )

    row2[2].metric(
        "Free Cash Flow",
        f"₹{fcf:.2f} Cr"
    )

    st.metric(
        "Composite Quality Score",
        f"{quality:.2f}"
    )


        # ==========================================================
    # Revenue vs Net Profit Chart
    # ==========================================================

    st.markdown("---")

    st.subheader("Revenue vs Net Profit (10 Years)")

    if not pl.empty:

        chart_df = pl.copy()

        chart_df["sales"] = chart_df["sales"].fillna(0)
        chart_df["net_profit"] = chart_df["net_profit"].fillna(0)

        revenue_chart = px.bar(
            chart_df,
            x="year",
            y=["sales", "net_profit"],
            barmode="group",
            title="Revenue vs Net Profit",
            labels={
                "year": "Financial Year",
                "value": "₹ Crore",
                "variable": "Metric",
            },
        )

        revenue_chart.update_layout(
            height=500,
            xaxis_title="Financial Year",
            yaxis_title="₹ Crore",
            legend_title="Metric",
        )

        st.plotly_chart(
            revenue_chart,
            use_container_width=True,
        )

    else:

        st.info("Revenue data not available.")

    # ==========================================================
    # ROE vs ROCE Trend
    # ==========================================================

    st.markdown("---")

    st.subheader("ROE vs ROCE Trend")

    if not ratios.empty:

        trend_df = ratios.copy()

        trend_df["return_on_equity_pct"] = (
            trend_df["return_on_equity_pct"]
            .fillna(0)
        )

        fig = make_subplots(
            specs=[[{"secondary_y": True}]]
        )

        fig.add_trace(
            go.Scatter(
                x=trend_df["year"],
                y=trend_df["return_on_equity_pct"],
                mode="lines+markers",
                name="ROE",
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                x=trend_df["year"],
                y=[roce] * len(trend_df),
                mode="lines+markers",
                name="ROCE",
            ),
            secondary_y=True,
        )

        fig.update_layout(
            height=500,
            legend_title="Metric",
        )

        fig.update_xaxes(
            title_text="Financial Year"
        )

        fig.update_yaxes(
            title_text="ROE (%)",
            secondary_y=False,
        )

        fig.update_yaxes(
            title_text="ROCE (%)",
            secondary_y=True,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        st.info("ROE trend data not available.")


        # ==========================================================
    # Pros & Cons
    # ==========================================================

    st.markdown("---")

    st.subheader("Pros & Cons")

    pros_col, cons_col = st.columns(2)

    with pros_col:

        st.success("Pros")

        pros = []

        if roe >= 15:
            pros.append("✅ Strong Return on Equity")

        if revenue_cagr >= 10:
            pros.append("✅ Healthy Revenue Growth")

        if pat_cagr >= 10:
            pros.append("✅ Strong PAT Growth")

        if eps_cagr >= 10:
            pros.append("✅ Strong EPS Growth")

        if debt <= 0.50:
            pros.append("✅ Low Debt")

        if fcf > 0:
            pros.append("✅ Positive Free Cash Flow")

        if interest >= 3:
            pros.append("✅ Healthy Interest Coverage")

        if quality >= 70:
            pros.append("✅ High Composite Quality Score")

        if len(pros) == 0:
            st.info("No major strengths identified.")

        else:

            for item in pros:
                st.write(item)

    with cons_col:

        st.error("Cons")

        cons = []

        if debt > 1:
            cons.append("❌ High Debt")

        if interest < 3:
            cons.append("❌ Low Interest Coverage")

        if npm < 5:
            cons.append("❌ Low Net Profit Margin")

        if revenue_cagr < 5:
            cons.append("❌ Weak Revenue Growth")

        if pat_cagr < 5:
            cons.append("❌ Weak PAT Growth")

        if eps_cagr < 5:
            cons.append("❌ Weak EPS Growth")

        if fcf < 0:
            cons.append("❌ Negative Free Cash Flow")

        if quality < 50:
            cons.append("❌ Low Composite Quality Score")

        if len(cons) == 0:
            st.info("No major weaknesses identified.")

        else:

            for item in cons:
                st.write(item)

    # ==========================================================
    # Balance Sheet
    # ==========================================================

    st.markdown("---")

    st.subheader("Balance Sheet")

    if not bs.empty:

        bs_display = (
            bs.sort_values(
                "year",
                ascending=False,
            )
            .fillna(0)
        )

        st.dataframe(
            bs_display,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("Balance Sheet data not available.")

    # ==========================================================
    # Cash Flow Statement
    # ==========================================================

    st.markdown("---")

    st.subheader("Cash Flow Statement")

    if not cf.empty:

        cf_display = (
            cf.sort_values(
                "year",
                ascending=False,
            )
            .fillna(0)
        )

        st.dataframe(
            cf_display,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("Cash Flow data not available.")

        # ==========================================================
    # Financial Summary
    # ==========================================================

    st.markdown("---")

    st.subheader("Financial Summary")

    summary_left, summary_right = st.columns(2)

    with summary_left:

        st.metric(
            "Revenue CAGR (5Y)",
            f"{revenue_cagr:.2f}%"
        )

        st.metric(
            "PAT CAGR (5Y)",
            f"{pat_cagr:.2f}%"
        )

        st.metric(
            "EPS CAGR (5Y)",
            f"{eps_cagr:.2f}%"
        )

    with summary_right:

        st.metric(
            "Interest Coverage",
            f"{interest:.2f}"
        )

        st.metric(
            "Debt / Equity",
            f"{debt:.2f}"
        )

        st.metric(
            "Composite Quality Score",
            f"{quality:.2f}"
        )

    # ==========================================================
    # About Company
    # ==========================================================

    st.markdown("---")

    st.subheader("About Company")

    about = company.get("about_company")

    if pd.notna(about):

        st.info(about)

    else:

        st.info("No company description available.")

    # ==========================================================
    # Useful Links
    # ==========================================================

    st.markdown("---")

    st.subheader("Useful Links")

    website = company.get("website")
    nse = company.get("nse_profile")
    bse = company.get("bse_profile")

    if pd.notna(website):
        st.markdown(f"🌐 **Website:** {website}")

    if pd.notna(nse):
        st.markdown(f"📈 **NSE Profile:** {nse}")

    if pd.notna(bse):
        st.markdown(f"🏛️ **BSE Profile:** {bse}")

    # ==========================================================
    # Download Financial Data
    # ==========================================================

    st.markdown("---")

    st.subheader("Download Financial Data")

    if not pl.empty:

        csv = pl.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Profit & Loss CSV",
            data=csv,
            file_name=f"{selected_company}_profit_loss.csv",
            mime="text/csv",
        )

    # ==========================================================
    # Footer
    # ==========================================================

    st.markdown("---")

    st.caption(
        "📊 N100 Financial Analytics Dashboard | Sprint 4 | Day 23"
    )