import streamlit as st
import pandas as pd
import requests

from utils.db import (
    get_companies,
    get_reports,
)

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Annual Reports",
    page_icon="📄",
    layout="wide",
)

# ==========================================================
# CSS
# ==========================================================

def inject_css():

    st.markdown(
        """
<style>

@keyframes fadeInUp{
from{opacity:0;transform:translateY(12px);}
to{opacity:1;transform:translateY(0);}
}

.main .block-container{
animation:fadeInUp .6s ease;
padding-top:2rem;
}

h1{
background:linear-gradient(90deg,#6C63FF,#FF6B9D,#FFB86C);
background-size:200% auto;
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
background-clip:text;
animation:gradient 6s linear infinite;
font-weight:800!important;
}

@keyframes gradient{
0%{background-position:0% center;}
100%{background-position:200% center;}
}

h2,h3{
font-weight:700!important;
border-left:4px solid #6C63FF;
padding-left:.6rem;
}

div[data-testid="stMetric"]{
background:linear-gradient(135deg,
rgba(108,99,255,.08),
rgba(255,107,157,.08));
border:1px solid rgba(108,99,255,.20);
border-radius:15px;
padding:14px;
box-shadow:0 4px 16px rgba(0,0,0,.08);
transition:.25s;
}

div[data-testid="stMetric"]:hover{
transform:translateY(-4px);
box-shadow:0 8px 22px rgba(108,99,255,.25);
}

div[data-testid="stDataFrame"]{
border-radius:14px;
overflow:hidden;
box-shadow:0 4px 16px rgba(0,0,0,.08);
}

div[data-testid="stExpander"]{
border-radius:14px;
}

div[data-testid="stDownloadButton"] button{
background:linear-gradient(90deg,#6C63FF,#FF6B9D);
color:white;
font-weight:700;
border:none;
border-radius:10px;
}

.report-ok{
background:#198754;
padding:5px 12px;
border-radius:20px;
color:white;
font-size:13px;
font-weight:700;
display:inline-block;
}

.report-bad{
background:#DC3545;
padding:5px 12px;
border-radius:20px;
color:white;
font-size:13px;
font-weight:700;
display:inline-block;
}

.pdf-card{

padding:16px;

border-radius:16px;

border:1px solid rgba(108,99,255,.18);

margin-bottom:14px;

box-shadow:0 3px 12px rgba(0,0,0,.05);

transition:.25s;

}

.pdf-card:hover{

transform:translateY(-4px);

box-shadow:0 8px 20px rgba(108,99,255,.18);

}

</style>
        """,
        unsafe_allow_html=True,
    )

# ==========================================================
# HELPERS
# ==========================================================

def divider():
    st.markdown("---")


def section(title):
    st.subheader(title)


def resolve_column(df, target_name):
    """
    Finds a column in df matching target_name, case-insensitively,
    and returns its actual name. Returns None if not found.
    Protects against KeyErrors when the DB returns 'year' instead
    of 'Year', 'annual_report' instead of 'Annual_Report', etc.
    """

    target_lower = target_name.lower()

    for col in df.columns:
        if col.lower() == target_lower:
            return col

    return None


def standardize_reports_columns(df):
    """
    Renames whichever casing/format the DB actually uses for the
    required columns into the exact names the rest of this page
    expects: company_id, Year, Annual_Report.
    """

    rename_map = {}

    for expected in ["company_id", "Year", "Annual_Report"]:
        actual = resolve_column(df, expected)
        if actual and actual != expected:
            rename_map[actual] = expected

    if rename_map:
        df = df.rename(columns=rename_map)

    return df


@st.cache_data(ttl=1800, show_spinner=False)
def check_pdf(url):
    """
    Checks whether a PDF/report URL is reachable.

    NOTE: BSE India blocks HTTP HEAD requests for many report URLs and
    returns a 404 for them even though the PDF itself opens fine in a
    browser. So for bseindia.com links we trust the URL's presence
    instead of verifying it over the network. For any other domain we
    still do a lightweight GET check.

    Cached so the same URL is only hit over the network once per 30
    minutes, instead of once per section on every rerun.
    """

    if pd.isna(url):
        return False

    url = str(url).strip()

    if url == "":
        return False

    # BSE blocks HEAD requests (and often GET verification too) -- if
    # the DB has a BSE link stored, treat it as available rather than
    # false-flagging it as unavailable.
    if "bseindia.com" in url.lower():
        return True

    try:

        response = requests.get(
            url,
            stream=True,
            timeout=5,
            allow_redirects=True,
        )

        return response.status_code == 200

    except Exception:

        return False


def availability_badge(status):

    if status:

        return (
            '<span class="report-ok">'
            'Available'
            '</span>'
        )

    return (
        '<span class="report-bad">'
        'Unavailable'
        '</span>'
    )


def show():

    # ==========================================================
    # PAGE START
    # ==========================================================

    inject_css()

    st.title("📄 Annual Reports")

    # ==========================================================
    # LOAD DATA
    # ==========================================================

    companies = get_companies()
    reports = get_reports()

    if companies.empty:
        st.error("Companies table not found.")
        st.stop()

    if reports.empty:
        st.error("No Annual Reports found in database.")
        st.stop()

    # Normalize column casing so 'year'/'Year', 'annual_report'/'Annual_Report',
    # 'company_id'/'CompanyID' etc. all resolve to what this page expects.
    reports = standardize_reports_columns(reports)

    id_col = resolve_column(companies, "id")
    company_id_col = resolve_column(companies, "company_id")

    if company_id_col is None and id_col is not None:
        companies = companies.rename(columns={id_col: "company_id"})

    name_col = resolve_column(companies, "company_name")
    if name_col and name_col != "company_name":
        companies = companies.rename(columns={name_col: "company_name"})

    # Guard against missing required columns
    required_report_cols = {"company_id", "Year", "Annual_Report"}
    missing_cols = required_report_cols - set(reports.columns)

    if missing_cols:
        st.error(f"Reports table is missing required column(s): {', '.join(sorted(missing_cols))}")
        st.stop()

    if "company_id" not in companies.columns or "company_name" not in companies.columns:
        st.error("Companies table must contain 'company_id' and 'company_name' columns.")
        st.stop()

    reports = reports.merge(

        companies[
            [
                "company_id",
                "company_name",
            ]
        ],

        on="company_id",

        how="left",

    )

    reports["company_name"] = reports["company_name"].fillna("Unknown")

    reports = reports.sort_values(

        [
            "company_name",
            "Year",
        ],

        ascending=[True, False],

    )

    # ==========================================================
    # SIDEBAR
    # ==========================================================

    st.sidebar.header("📑 Filters")

    company_names = (
        reports["company_name"]
        .dropna()
        .sort_values()
        .unique()
        .tolist()
    )

    search_text = st.sidebar.text_input(
        "🔍 Search Company",
        placeholder="Type company..."
    )

    if search_text:

        company_names = [

            c

            for c in company_names

            if search_text.lower() in c.lower()

        ]

    if not company_names:
        st.sidebar.warning("No companies match your search.")
        st.warning("No companies match your search term. Try a different name.")
        st.stop()

    selected_company = st.sidebar.selectbox(

        "Select Company",

        company_names,

    )

    # ==========================================================
    # FILTER COMPANY
    # ==========================================================

    company_reports = reports[
        reports["company_name"] == selected_company
    ].copy()

    company_reports = company_reports.sort_values(
        "Year",
        ascending=False,
    )

    # ==========================================================
    # YEAR FILTER
    # ==========================================================

    available_years = (
        company_reports["Year"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_years = st.sidebar.multiselect(

        "Select Year(s)",

        available_years,

        default=available_years,

    )

    if selected_years:

        company_reports = company_reports[
            company_reports["Year"].isin(selected_years)
        ]

    divider()

    section("📊 Report Summary")

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Company",
            selected_company,
        )

    with c2:

        st.metric(
            "Reports Found",
            len(company_reports),
        )

    divider()

    # ==========================================================
    # REPORT LIST
    # ==========================================================

    section("📂 Available Annual Reports")

    # Initialized here (not inside the else-branch) so later sections
    # can safely reference these counts even if company_reports is empty.
    available_count = 0
    unavailable_count = 0

    # Pre-compute PDF availability once per row and reuse everywhere
    # below, instead of re-checking the same URL multiple times.
    if not company_reports.empty:
        company_reports["_report_ok"] = company_reports["Annual_Report"].apply(check_pdf)
        available_count = int(company_reports["_report_ok"].sum())
        unavailable_count = int((~company_reports["_report_ok"]).sum())

    if company_reports.empty:

        st.warning(
            "No Annual Reports available for the selected filters."
        )

    else:

        for _, row in company_reports.iterrows():

            report_url = row["Annual_Report"]
            report_ok = row["_report_ok"]

            with st.container():

                st.markdown(
                    '<div class="pdf-card">',
                    unsafe_allow_html=True,
                )

                left, right = st.columns([5, 2])

                with left:

                    st.markdown(
                        f"### 📅 {row['Year']}"
                    )

                    st.markdown(
                        availability_badge(report_ok),
                        unsafe_allow_html=True,
                    )

                    st.write("")

                    if report_ok:

                        st.markdown(
                            f"""
    <a href="{report_url}" target="_blank">
    Open Annual Report (PDF)
    </a>
                            """,
                            unsafe_allow_html=True,
                        )

                    else:

                        st.error(
                            "Report unavailable or BSE link is invalid."
                        )

                with right:

                    if report_ok:

                        st.success("Ready")

                    else:

                        st.error("404")

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True,
                )

    # ==========================================================
    # SUMMARY
    # ==========================================================

    divider()

    section("📈 Report Statistics")

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Total Reports",
        len(company_reports),
    )

    m2.metric(
        "Available",
        available_count,
    )

    m3.metric(
        "Unavailable",
        unavailable_count,
    )

    divider()

    # ==========================================================
    # YEAR-WISE REPORT TABLE
    # ==========================================================

    section("📋 Report History")

    if company_reports.empty:

        st.info("No report history to display.")

    else:

        table_df = company_reports.copy()

        table_df["Status"] = table_df["_report_ok"].map(
            {
                True: "🟢 Available",
                False: "🔴 Unavailable",
            }
        )

        table_df = table_df[
            [
                "Year",
                "Status",
                "Annual_Report",
            ]
        ]

        table_df = table_df.rename(
            columns={
                "Annual_Report": "PDF Link",
            }
        )

        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
        )

    # ==========================================================
    # QUICK SEARCH
    # ==========================================================

    divider()

    section("🔎 Find Report")

    search_year = st.text_input(
        "Enter Report Year",
        placeholder="Example : 2023"
    )

    if search_year:

        search_df = company_reports[
            company_reports["Year"]
            .astype(str)
            .str.contains(search_year, case=False, na=False)
        ]

        if search_df.empty:

            st.warning(
                "No report found."
            )

        else:

            st.success(
                f"{len(search_df)} report(s) found."
            )

            st.dataframe(

                search_df[
                    [
                        "Year",
                        "Annual_Report",
                    ]
                ],

                hide_index=True,

                use_container_width=True,

            )

    divider()

    # ==========================================================
    # DOWNLOAD / OPEN LINKS
    # ==========================================================

    section("📥 Open Reports")

    if company_reports.empty:

        st.info("No reports to open for the current selection.")

    else:

        for _, row in company_reports.iterrows():

            pdf = row["Annual_Report"]

            year = row["Year"]

            ok = row["_report_ok"]

            if ok:

                st.link_button(

                    f"📄 Open {year} Annual Report",

                    pdf,

                    use_container_width=True,

                )

            else:

                st.button(

                    f"❌ {year} Report Unavailable",

                    disabled=True,

                    use_container_width=True,

                    key=f"unavailable_{year}",

                )


    # ==========================================================
    # DASHBOARD KPIs
    # ==========================================================

    divider()

    section("📊 Dashboard Summary")

    k1, k2, k3, k4 = st.columns(4)

    total_reports = len(company_reports)

    latest_report = (
        company_reports["Year"].max()
        if total_reports > 0
        else "-"
    )

    k1.metric(
        "Total Reports",
        total_reports,
    )

    k2.metric(
        "Available",
        available_count,
    )

    k3.metric(
        "Unavailable",
        unavailable_count,
    )

    k4.metric(
        "Latest Report",
        latest_report,
    )

    # ==========================================================
    # REPORTS BY YEAR
    # ==========================================================

    divider()

    section("📈 Reports Timeline")

    if company_reports.empty:

        st.info("No data available for the timeline.")

    else:

        timeline = (
            company_reports
            .groupby("Year")
            .size()
            .reset_index(name="Reports")
            .sort_values("Year")
        )

        if not timeline.empty:

            st.bar_chart(
                timeline.set_index("Year")
            )


    # ==========================================================
    # DATASET INFORMATION
    # ==========================================================

    divider()

    with st.expander("ℹ Dataset Information", expanded=False):

        st.write("### Database")

        st.write(
            """
    **Tables Used**

    • companies

    • documents
    """
        )

        st.write("### Source")

        st.info(
            """
    Annual Reports are fetched from
    the **BSE India** document links
    stored in the database.
    """
        )

        st.write("### Selected Company")

        st.write(selected_company)

        st.write("### Available Years")

        if not company_reports.empty:

            st.write(
                sorted(
                    company_reports["Year"]
                    .unique(),
                    reverse=True,
                )
            )

        else:

            st.write("No years available for this selection.")

    # ==========================================================
    # FOOTER
    # ==========================================================

    divider()

    st.caption(
        """
    📄 N100 Financial Analytics Dashboard

    Sprint 4 • Day 25

    Annual Reports Module

    Data Source : BSE India
    """
    )


if __name__ == "__main__":
    show()