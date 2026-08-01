import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.db import (
    get_companies,
    get_ratios,
    get_peers,
)


# =====================================================
# Styling (CSS + animations) - same treatment as
# the main dashboard page
# =====================================================

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

        /* ---------- Divider (st.markdown("---")) ---------- */
        hr {
            margin-top: 1.2rem;
            margin-bottom: 1.2rem;
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #6C63FF, transparent);
            animation: fadeInUp 0.8s ease-out;
        }

        /* ---------- Charts, dataframe & expander containers ---------- */
        div[data-testid="stPlotlyChart"],
        div[data-testid="stDataFrame"],
        div[data-testid="stExpander"] {
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
            transition: box-shadow 0.25s ease, transform 0.25s ease;
            animation: fadeInUp 0.8s ease-out;
        }

        div[data-testid="stPlotlyChart"]:hover,
        div[data-testid="stDataFrame"]:hover {
            box-shadow: 0 10px 26px rgba(0,0,0,0.12);
            transform: translateY(-3px);
        }

        /* ---------- Selectboxes ---------- */
        div[data-testid="stSelectbox"] label {
            font-weight: 700;
            color: #6C63FF;
        }

        div[data-baseweb="select"] {
            border-radius: 10px !important;
            transition: box-shadow 0.25s ease;
        }

        div[data-baseweb="select"]:hover {
            box-shadow: 0 0 0 2px rgba(108,99,255,0.3);
        }

        /* ---------- Success / info banners (benchmark callouts) ---------- */
        div[data-testid="stAlert"] {
            border-radius: 12px;
            animation: fadeInUp 0.6s ease-out;
            transition: transform 0.2s ease;
        }

        div[data-testid="stAlert"]:hover {
            transform: translateY(-2px);
        }

        /* ---------- Download button ---------- */
        div[data-testid="stDownloadButton"] button {
            border-radius: 10px;
            font-weight: 700;
            background: linear-gradient(90deg, #6C63FF, #FF6B9D);
            color: white;
            border: none;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        div[data-testid="stDownloadButton"] button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 18px rgba(108,99,255,0.35);
        }

        /* ---------- Caption / footer ---------- */
        .stCaption, [data-testid="stCaptionContainer"] {
            opacity: 0.7;
            animation: fadeInUp 0.9s ease-out;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def styled_divider():
    """Thin gradient divider, replacing plain st.markdown('---')."""
    st.markdown("<hr/>", unsafe_allow_html=True)


# =====================================================
# Safe Helper
# =====================================================

def safe_series(df, column, default=0):

    if column not in df.columns:
        return pd.Series(
            [default] * len(df)
        )

    return df[column].fillna(default)


# =====================================================
# Peer Comparison Screen
# =====================================================

def show():

    inject_css()

    st.title("👥 Peer Comparison")

    # -------------------------------------------------
    # Load Database
    # -------------------------------------------------

    companies = get_companies()

    ratios = get_ratios()

    peers = get_peers()

    if companies.empty:

        st.warning("Company data not available.")

        st.stop()

    if ratios.empty:

        st.warning("Financial ratio data not available.")

        st.stop()

    if peers.empty:

        st.warning("Peer group data not available.")

        st.stop()

    # -------------------------------------------------
    # IMPORTANT FIX
    # Get latest financial record FOR EACH COMPANY
    # -------------------------------------------------

    ratios["year_dt"] = pd.to_datetime(

        ratios["year"],

        format="%b %Y",

        errors="coerce",

    )

    ratios = (

        ratios

        .sort_values("year_dt")

        .groupby("company_id", as_index=False)

        .tail(1)

        .drop(columns="year_dt")

    )

    # -------------------------------------------------
    # Add Company Name into Ratios
    # -------------------------------------------------

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

    ratios = ratios.drop(
        columns=["id"],
        errors="ignore",
    )

    # -------------------------------------------------
    # Add Company Name into Peers
    # -------------------------------------------------

    peers = peers.merge(

        companies[
            [
                "id",
                "company_name",
            ]
        ],

        left_on="company_id",

        right_on="id",

        how="left",

        suffixes=("", "_drop"),

    )

    peers = peers.drop(
        columns=["id"],
        errors="ignore",
    )

        # =====================================================
    # Peer Group Selection
    # =====================================================

    peer_groups = sorted(
        peers["peer_group_name"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_group = st.selectbox(
        "Select Peer Group",
        peer_groups,
    )

    group_df = peers[
        peers["peer_group_name"] == selected_group
    ].copy()

    if group_df.empty:

        st.warning(
            "No companies found in this peer group."
        )

        st.stop()

    # =====================================================
    # Company Selection
    # =====================================================

    company_list = sorted(
        group_df["company_name"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_company = st.selectbox(
        "Select Company",
        company_list,
    )

    # =====================================================
    # Benchmark Company
    # =====================================================

    benchmark_name = None

    benchmark = group_df[
        group_df["is_benchmark"] == 1
    ]

    if not benchmark.empty:

        benchmark_name = benchmark.iloc[0][
            "company_name"
        ]

        st.success(
            f"🏆 Benchmark Company: {benchmark_name}"
        )

    # =====================================================
    # Merge Peer Companies with Latest Ratios
    # =====================================================

    compare_df = group_df.merge(

        ratios,

        on="company_id",

        how="left",

        suffixes=("", "_ratio"),

    )

    # =====================================================
    # Fill Missing Values
    # =====================================================

    metric_columns = [

        "return_on_equity_pct",

        "operating_profit_margin_pct",

        "net_profit_margin_pct",

        "debt_to_equity",

        "interest_coverage",

        "free_cash_flow_cr",

        "revenue_cagr_5yr",

        "composite_quality_score",

    ]

    for column in metric_columns:

        compare_df[column] = safe_series(
            compare_df,
            column,
        )

    # =====================================================
    # Selected Company
    # =====================================================

    selected = compare_df[
        compare_df["company_name"] == selected_company
    ]

    if selected.empty:

        st.warning(
            "Selected company data not available."
        )

        st.stop()

    selected = selected.iloc[0]

    # =====================================================
    # Peer Average
    # =====================================================

    peer_average = compare_df[
        metric_columns
    ].mean()

        # =====================================================
    # Radar Chart
    # =====================================================

    styled_divider()

    st.subheader("📊 Company vs Peer Average")

    radar_metrics = [

        "return_on_equity_pct",

        "operating_profit_margin_pct",

        "net_profit_margin_pct",

        "interest_coverage",

        "revenue_cagr_5yr",

        "free_cash_flow_cr",

        "debt_to_equity",

        "composite_quality_score",

    ]

    radar_labels = [

        "ROE",

        "OPM",

        "Net Margin",

        "Interest Cover",

        "Revenue CAGR",

        "Free Cash Flow",

        "Debt / Equity",

        "Quality Score",

    ]

    company_values = []

    peer_values = []

    for metric in radar_metrics:

        company_values.append(
            float(selected[metric])
        )

        peer_values.append(
            float(peer_average[metric])
        )

    # Close polygon

    company_values.append(company_values[0])

    peer_values.append(peer_values[0])

    radar_labels_closed = radar_labels.copy()

    radar_labels_closed.append(
        radar_labels[0]
    )

    radar_chart = go.Figure()

    radar_chart.add_trace(

        go.Scatterpolar(

            r=company_values,

            theta=radar_labels_closed,

            fill="toself",

            name=selected_company,

            line=dict(width=3, color="#6C63FF"),

            fillcolor="rgba(108,99,255,0.25)",

        )

    )

    radar_chart.add_trace(

        go.Scatterpolar(

            r=peer_values,

            theta=radar_labels_closed,

            fill="toself",

            name="Peer Average",

            line=dict(width=3, color="#FF6B9D"),

            fillcolor="rgba(255,107,157,0.20)",

        )

    )

    radar_chart.update_layout(

        title=f"{selected_company} vs Peer Average",

        height=650,

        showlegend=True,

        legend=dict(orientation="h", yanchor="bottom", y=-0.15),

        margin=dict(t=60, b=20, l=40, r=40),

        polar=dict(

            bgcolor="rgba(108,99,255,0.03)",

            radialaxis=dict(

                visible=True,

                showline=True,

                gridcolor="rgba(108,99,255,0.15)",

            ),

            angularaxis=dict(
                gridcolor="rgba(108,99,255,0.15)",
            ),

        ),

    )

    st.plotly_chart(

        radar_chart,

        use_container_width=True,

    )

    # =====================================================
    # Quick KPI Cards
    # =====================================================

    styled_divider()

    st.subheader("📈 Selected Company Snapshot")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "ROE",
        f"{selected['return_on_equity_pct']:.2f}%"
    )

    c2.metric(
        "Revenue CAGR",
        f"{selected['revenue_cagr_5yr']:.2f}%"
    )

    c3.metric(
        "Debt / Equity",
        f"{selected['debt_to_equity']:.2f}"
    )

    c4.metric(
        "Quality Score",
        f"{selected['composite_quality_score']:.2f}"
    )

        # =====================================================
    # Peer Comparison Table
    # =====================================================

    styled_divider()

    st.subheader("📋 Peer Comparison Table")

    table = compare_df[
        [
            "company_name",
            "return_on_equity_pct",
            "operating_profit_margin_pct",
            "net_profit_margin_pct",
            "debt_to_equity",
            "interest_coverage",
            "revenue_cagr_5yr",
            "free_cash_flow_cr",
            "composite_quality_score",
            "is_benchmark",
        ]
    ].copy()

    table = table.rename(
        columns={
            "company_name": "Company",
            "return_on_equity_pct": "ROE (%)",
            "operating_profit_margin_pct": "OPM (%)",
            "net_profit_margin_pct": "Net Margin (%)",
            "debt_to_equity": "Debt / Equity",
            "interest_coverage": "Interest Coverage",
            "revenue_cagr_5yr": "Revenue CAGR (%)",
            "free_cash_flow_cr": "FCF (Cr)",
            "composite_quality_score": "Quality Score",
        }
    )

    # Hide helper column from display
    display_table = table.drop(
        columns=["is_benchmark"]
)

    # -----------------------------------------------------
    # Highlight Benchmark Row
    # -----------------------------------------------------

    def highlight_benchmark(row):

        if row["is_benchmark"] == 1:

            return [
                "background-color:#d4edda; font-weight:bold;"
            ] * len(row)

        return [""] * len(row)

    styled_table = (

    display_table.style

    .apply(

        lambda row: (
            ["background-color:#d4edda; font-weight:bold;"] * len(row)
            if table.loc[row.name, "is_benchmark"] == 1
            else [""] * len(row)
        ),

        axis=1,

    )

    .format(
        {
            "ROE (%)": "{:.2f}",
            "OPM (%)": "{:.2f}",
            "Net Margin (%)": "{:.2f}",
            "Debt / Equity": "{:.2f}",
            "Interest Coverage": "{:.2f}",
            "Revenue CAGR (%)": "{:.2f}",
            "FCF (Cr)": "{:.2f}",
            "Quality Score": "{:.2f}",
        }
    )

)

    st.dataframe(

        styled_table,

        use_container_width=True,

        hide_index=True,

    )

    # -----------------------------------------------------
    # Remove helper column for download
    # -----------------------------------------------------

    download_table = display_table.copy()

    # -----------------------------------------------------
    # Statistics
    # -----------------------------------------------------

    styled_divider()

    st.subheader("📊 Peer Statistics")

    s1, s2, s3 = st.columns(3)

    s1.metric(
        "Companies",
        len(download_table)
    )

    s2.metric(
        "Average ROE",
        f"{download_table['ROE (%)'].mean():.2f}%"
    )

    s3.metric(
        "Average Quality Score",
        f"{download_table['Quality Score'].mean():.2f}"
    )

        # =====================================================
    # Download CSV
    # =====================================================

    styled_divider()

    csv = download_table.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(

        label="📥 Download Peer Comparison CSV",

        data=csv,

        file_name=f"{selected_group}_peer_comparison.csv",

        mime="text/csv",

    )

    # =====================================================
    # Benchmark Summary
    # =====================================================

    styled_divider()

    st.subheader("🏆 Benchmark Company")

    if benchmark_name is not None:

        benchmark_data = compare_df[
            compare_df["company_name"] == benchmark_name
        ]

        if not benchmark_data.empty:

            benchmark_data = benchmark_data.iloc[0]

            b1, b2, b3, b4 = st.columns(4)

            b1.metric(
                "Benchmark",
                benchmark_name,
            )

            b2.metric(
                "ROE",
                f"{benchmark_data['return_on_equity_pct']:.2f}%"
            )

            b3.metric(
                "Revenue CAGR",
                f"{benchmark_data['revenue_cagr_5yr']:.2f}%"
            )

            b4.metric(
                "Quality Score",
                f"{benchmark_data['composite_quality_score']:.2f}"
            )

    else:

        st.info(
            "No benchmark company available for this peer group."
        )

    # =====================================================
    # Dataset Summary
    # =====================================================

    styled_divider()

    with st.expander("📊 Dataset Summary"):

        st.write(
            f"**Peer Group:** {selected_group}"
        )

        st.write(
            f"**Companies:** {len(compare_df)}"
        )

        st.write(
            "**Metrics Used:**"
        )

        st.markdown("""

- Return on Equity (ROE)

- Operating Profit Margin (OPM)

- Net Profit Margin

- Debt / Equity

- Interest Coverage

- Revenue CAGR (5Y)

- Free Cash Flow

- Composite Quality Score

""")

    # =====================================================
    # Footer
    # =====================================================

    styled_divider()

    st.caption(
        "📊 N100 Financial Analytics Dashboard | Sprint 4 | Day 24 | Peer Comparison"
    )