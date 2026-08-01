import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import (
    get_companies,
    get_ratios,
    get_sectors,
)


# =========================================================
# CSS Styling
# =========================================================

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

    inject_css()

    st.title("🏢 Sector Analysis")

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
    # Latest Financial Year
    # -----------------------------------------------------

    latest_year = df["year"].max()

    df = df[
        df["year"] == latest_year
    ].copy()

    # -----------------------------------------------------
    # Sidebar
    # -----------------------------------------------------

    st.sidebar.header("Sector Filters")

    sector_list = sorted(

        df["broad_sector"]
        .dropna()
        .unique()
        .tolist()

    )

    selected_sector = st.sidebar.selectbox(

        "Select Sector",

        sector_list,

    )

    # -----------------------------------------------------
    # Filter Sector
    # -----------------------------------------------------

    sector_df = df[
        df["broad_sector"] == selected_sector
    ].copy()

    if sector_df.empty:

        st.warning(
            "No companies available."
        )

        st.stop()

    # -----------------------------------------------------
    # KPI Cards
    # -----------------------------------------------------

    st.subheader(selected_sector)

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
    # Bubble Chart
    # -----------------------------------------------------

    st.subheader("📈 Sector Bubble Chart")

    st.caption(
        "X = Revenue CAGR | Y = ROE | Bubble Size = Quality Score | Colour = Sub Sector"
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

    bubble_df["composite_quality_score"] = (
        bubble_df["composite_quality_score"]
        .fillna(10)
    )

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

        size="composite_quality_score",

        color="sub_sector",

        hover_name="company_name",

        hover_data={

            "revenue_cagr_5yr": ":.2f",

            "return_on_equity_pct": ":.2f",

            "composite_quality_score": ":.2f",

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

    st.download_button(
        label="Download Sector Analysis (CSV)",
        data=csv,
        file_name=f"{selected_sector.lower().replace(' ','_')}_sector_analysis.csv",
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
            f"**Financial Year:** {latest_year}"
        )

        st.write(
            f"**Selected Sector:** {selected_sector}"
        )

        st.write(
            f"**Companies in Sector:** {len(sector_df)}"
        )

        st.write(
            f"**Total Companies:** {len(df)}"
        )

        st.markdown(
            """
### Bubble Chart

- **X Axis:** Revenue CAGR (5 Years)
- **Y Axis:** Return on Equity (ROE)
- **Bubble Size:** Composite Quality Score
- **Bubble Colour:** Sub Sector

### Data Sources

- Companies
- Financial Ratios
- Sectors

> Note: Market Capitalization data is not available in the current database, so Composite Quality Score is used as the bubble size.
            """
        )

    divider()

    # -----------------------------------------------------
    # Footer
    # -----------------------------------------------------

    st.caption(
        "📊 N100 Financial Analytics Dashboard | Sprint 4 | Day 25 | Sector Analysis"
    )