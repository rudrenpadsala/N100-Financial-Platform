"""
Nifty 100 Analytics Dashboard
Main Streamlit Application
"""

import streamlit as st

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------

st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------

st.sidebar.title("📊 Nifty 100 Analytics")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Company Profile",
        "Screener",
        "Peer Comparison",
        "Trend Analysis",
        "Sector Analysis",
        "Capital Allocation",
        "Annual Reports",
    ],
)

# ---------------------------------------------------
# Import Pages
# ---------------------------------------------------

from src.dashboard.pages import (
    home,
    profile,
    screener,
    peers,
    trends,
    sectors,
    capital,
    reports,
)

# ---------------------------------------------------
# Navigation
# ---------------------------------------------------

if page == "Home":
    home.show()

elif page == "Company Profile":
    profile.show()

elif page == "Screener":
    screener.show()

elif page == "Peer Comparison":
    peers.show()

elif page == "Trend Analysis":
    trends.show()

elif page == "Sector Analysis":
    sectors.show()

elif page == "Capital Allocation":
    capital.show()

elif page == "Annual Reports":
    reports.show()