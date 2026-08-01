import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.db import (
    get_companies,
    get_ratios,
)


# =====================================================
# CSS Styling
# =====================================================

def inject_css():

    st.markdown(
        """
<style>

@keyframes fadeInUp{
from{
opacity:0;
transform:translateY(14px);
}
to{
opacity:1;
transform:translateY(0);
}
}

.main .block-container{
animation:fadeInUp .6s ease-out;
padding-top:2rem;
}

h1{
background:linear-gradient(
90deg,
#6C63FF,
#FF6B9D,
#FFB86C
);

background-size:200% auto;

-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
background-clip:text;

font-weight:800!important;

animation:shimmer 6s linear infinite;
}

@keyframes shimmer{

0%{
background-position:0%;
}

100%{
background-position:200%;
}

}

h2,h3{

font-weight:700!important;

border-left:4px solid #6C63FF;

padding-left:.6rem;

animation:fadeInUp .6s ease-out;

}

div[data-testid="stMetric"]{

background:
linear-gradient(
135deg,
rgba(108,99,255,.08),
rgba(255,107,157,.08)
);

border:1px solid rgba(108,99,255,.25);

border-radius:16px;

padding:1rem;

box-shadow:0 4px 14px rgba(0,0,0,.06);

transition:.25s;

animation:fadeInUp .7s ease-out;

}

div[data-testid="stMetric"]:hover{

transform:translateY(-5px);

box-shadow:0 10px 24px rgba(108,99,255,.25);

border-color:#6C63FF;

}

div[data-testid="stMetricLabel"]{

font-weight:600;

opacity:.75;

}

div[data-testid="stMetricValue"]{

font-size:1.6rem!important;

font-weight:800!important;

}

hr{

margin-top:1rem;

margin-bottom:1rem;

border:none;

height:2px;

background:
linear-gradient(
90deg,
transparent,
#6C63FF,
transparent
);

}

div[data-testid="stPlotlyChart"],
div[data-testid="stDataFrame"]{

border-radius:16px;

overflow:hidden;

box-shadow:0 4px 16px rgba(0,0,0,.06);

transition:.25s;

animation:fadeInUp .8s ease-out;

}

div[data-testid="stPlotlyChart"]:hover,
div[data-testid="stDataFrame"]:hover{

transform:translateY(-3px);

box-shadow:0 10px 26px rgba(0,0,0,.12);

}

section[data-testid="stSidebar"]{

background:
linear-gradient(
180deg,
rgba(108,99,255,.05),
rgba(255,107,157,.03)
);

}

section[data-testid="stSidebar"] label{

font-weight:700;

color:#6C63FF;

}

div[data-testid="stDownloadButton"] button{

background:
linear-gradient(
90deg,
#6C63FF,
#FF6B9D
);

color:white;

font-weight:700;

border:none;

border-radius:10px;

transition:.25s;

}

div[data-testid="stDownloadButton"] button:hover{

transform:translateY(-3px);

box-shadow:0 8px 18px rgba(108,99,255,.35);

}

</style>
""",
unsafe_allow_html=True,
)


# =====================================================
# Helper Functions
# =====================================================

def divider():
    st.markdown("<hr/>", unsafe_allow_html=True)


def safe_series(df, column, default=0):
    if column not in df.columns:
        return pd.Series([default] * len(df))

    return df[column].fillna(default)


def calculate_yoy(series):
    """
    Returns Year-over-Year percentage change.
    """

    return series.pct_change() * 100


def format_number(value):

    if pd.isna(value):
        return "0"

    if abs(value) >= 1000:
        return f"{value:,.0f}"

    return f"{value:.2f}"


def safe_float(value):

    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except Exception:
        return 0.0

# =====================================================
# Trend Analysis Page
# =====================================================

def show():

    inject_css()

    st.title("📈 Trend Analysis")

    # -------------------------------------------------
    # Load Data
    # -------------------------------------------------

    companies = get_companies()
    ratios = get_ratios()

    if companies.empty or ratios.empty:

        st.warning("Financial data not available.")

        st.stop()

    # -------------------------------------------------
    # Merge Company Names
    # -------------------------------------------------

    companies = companies.rename(
        columns={"id": "company_id"}
    )

    ratios = ratios.merge(

        companies[
            [
                "company_id",
                "company_name",
            ]
        ],

        on="company_id",

        how="left",

    )

    # -------------------------------------------------
    # Sidebar
    # -------------------------------------------------

    st.sidebar.header("Trend Settings")

    company_list = sorted(
        ratios["company_name"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_company = st.sidebar.selectbox(
        "Select Company",
        company_list,
    )

    # -------------------------------------------------
    # Company Data
    # -------------------------------------------------

    company_df = ratios[
        ratios["company_name"] == selected_company
    ].copy()

    if company_df.empty:

        st.error(
            "Company data not found."
        )

        st.stop()

    # -------------------------------------------------
    # Sort Years
    # -------------------------------------------------

    company_df = company_df.sort_values(
        "year"
    )

    # -------------------------------------------------
    # Available Metrics
    # -------------------------------------------------

    metric_map = {

        "Revenue CAGR":
            "revenue_cagr_5yr",

        "PAT CAGR":
            "pat_cagr_5yr",

        "EPS CAGR":
            "eps_cagr_5yr",

        "ROE":
            "return_on_equity_pct",

        "Net Profit Margin":
            "net_profit_margin_pct",

        "Operating Margin":
            "operating_profit_margin_pct",

        "Debt / Equity":
            "debt_to_equity",

        "Interest Coverage":
            "interest_coverage",

        "Free Cash Flow":
            "free_cash_flow_cr",

        "Quality Score":
            "composite_quality_score",

    }

    selected_metrics = st.sidebar.multiselect(

        "Select up to 3 Metrics",

        list(metric_map.keys()),

        default=[
            "ROE",
            "Revenue CAGR",
        ],

        max_selections=3,

    )

    if len(selected_metrics) == 0:

        st.info(
            "Please select at least one metric."
        )

        st.stop()
        # -------------------------------------------------
    # KPI Cards
    # -------------------------------------------------

    st.subheader(selected_company)

    latest = company_df.iloc[-1]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "ROE",
        f"{latest['return_on_equity_pct']:.2f}%"
    )

    c2.metric(
        "Revenue CAGR",
        f"{latest['revenue_cagr_5yr']:.2f}%"
    )

    c3.metric(
        "Quality Score",
        f"{latest['composite_quality_score']:.2f}"
    )

    st.divider()

    # -------------------------------------------------
    # Multi Metric Trend Chart
    # -------------------------------------------------

    fig = go.Figure()

    colors = [
        "#636EFA",
        "#EF553B",
        "#00CC96",
    ]

    for i, metric_name in enumerate(selected_metrics):

        column = metric_map[metric_name]

        y = company_df[column].fillna(0)

        fig.add_trace(

            go.Scatter(

                x=company_df["year"],

                y=y,

                mode="lines+markers",

                name=metric_name,

                line=dict(
                    width=3,
                    color=colors[i]
                ),

                marker=dict(
                    size=8
                )

            )

        )

        # ---------------------------------------------
        # YoY Annotation
        # ---------------------------------------------

        yoy = y.pct_change() * 100

        for x, value, change in zip(
            company_df["year"],
            y,
            yoy,
        ):

            if pd.notna(change):

                fig.add_annotation(

                    x=x,

                    y=value,

                    text=f"{change:.1f}%",

                    showarrow=False,

                    yshift=12,

                    font=dict(
                        size=10,
                        color=colors[i]
                    )

                )

        # -------------------------------------------------
    # Chart Layout
    # -------------------------------------------------

    fig.update_layout(

        title="10-Year Financial Trend",

        xaxis_title="Financial Year",

        yaxis_title="Value",

        hovermode="x unified",

        height=650,

        template="plotly_white",

        legend=dict(

            orientation="h",

            yanchor="bottom",

            y=1.02,

            xanchor="right",

            x=1,

        ),

        margin=dict(

            l=20,

            r=20,

            t=60,

            b=20,

        ),

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

    st.divider()

    # -------------------------------------------------
    # Financial Data Table
    # -------------------------------------------------

    st.subheader("Financial Data")

    display_df = company_df[

        [

            "year",

            "return_on_equity_pct",

            "net_profit_margin_pct",

            "operating_profit_margin_pct",

            "debt_to_equity",

            "interest_coverage",

            "revenue_cagr_5yr",

            "pat_cagr_5yr",

            "eps_cagr_5yr",

            "free_cash_flow_cr",

            "composite_quality_score",

        ]

    ].copy()

    display_df.columns = [

        "Year",

        "ROE (%)",

        "Net Profit Margin (%)",

        "Operating Margin (%)",

        "Debt / Equity",

        "Interest Coverage",

        "Revenue CAGR (%)",

        "PAT CAGR (%)",

        "EPS CAGR (%)",

        "Free Cash Flow (Cr)",

        "Quality Score",

    ]

    st.dataframe(

        display_df,

        use_container_width=True,

        hide_index=True,

    )

    # -------------------------------------------------
    # Download CSV
    # -------------------------------------------------

    csv = display_df.to_csv(

        index=False

    ).encode("utf-8")

    st.download_button(

        label="📥 Download Trend Data",

        data=csv,

        file_name=f"{selected_company}_trend.csv",

        mime="text/csv",

    )

    # -------------------------------------------------
    # Footer
    # -------------------------------------------------

    st.divider()

    st.caption(

        "📈 N100 Financial Analytics Dashboard | Sprint 4 | Day 25 | Trend Analysis"

    )
    