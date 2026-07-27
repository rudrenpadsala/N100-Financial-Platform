"""
Shared SQLite data loader
Used by every Streamlit screen
"""

import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "db/nifty100.db"


# -----------------------------------------------------
# Connection
# -----------------------------------------------------

def get_connection():
    return sqlite3.connect(DB_PATH)


# -----------------------------------------------------
# Companies
# -----------------------------------------------------

@st.cache_data(ttl=600)
def get_companies():

    conn = get_connection()

    query = """
    SELECT *
    FROM companies
    ORDER BY company_name
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# -----------------------------------------------------
# Financial Ratios
# -----------------------------------------------------

@st.cache_data(ttl=600)
def get_ratios(ticker, year=None):

    conn = get_connection()

    if year is None:

        query = """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year
        """

        df = pd.read_sql(
            query,
            conn,
            params=(ticker,)
        )

    else:

        query = """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        AND year = ?
        """

        df = pd.read_sql(
            query,
            conn,
            params=(ticker, year)
        )

    conn.close()

    return df


# -----------------------------------------------------
# Profit & Loss
# -----------------------------------------------------

@st.cache_data(ttl=600)
def get_pl(ticker):

    conn = get_connection()

    query = """
    SELECT *
    FROM profitandloss
    WHERE company_id = ?
    ORDER BY year
    """

    df = pd.read_sql(
        query,
        conn,
        params=(ticker,)
    )

    conn.close()

    return df


# -----------------------------------------------------
# Balance Sheet
# -----------------------------------------------------

@st.cache_data(ttl=600)
def get_bs(ticker):

    conn = get_connection()

    query = """
    SELECT *
    FROM balancesheet
    WHERE company_id = ?
    ORDER BY year
    """

    df = pd.read_sql(
        query,
        conn,
        params=(ticker,)
    )

    conn.close()

    return df


# -----------------------------------------------------
# Cash Flow
# -----------------------------------------------------

@st.cache_data(ttl=600)
def get_cf(ticker):

    conn = get_connection()

    query = """
    SELECT *
    FROM cashflow
    WHERE company_id = ?
    ORDER BY year
    """

    df = pd.read_sql(
        query,
        conn,
        params=(ticker,)
    )

    conn.close()

    return df


# -----------------------------------------------------
# Sector Data
# -----------------------------------------------------

@st.cache_data(ttl=600)
def get_sectors():

    conn = get_connection()

    query = """
    SELECT *
    FROM sectors
    ORDER BY broad_sector
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# -----------------------------------------------------
# Peer Groups
# -----------------------------------------------------

@st.cache_data(ttl=600)
def get_peers(group_name):

    conn = get_connection()

    query = """
    SELECT *
    FROM peer_groups
    WHERE peer_group_name = ?
    """

    df = pd.read_sql(
        query,
        conn,
        params=(group_name,)
    )

    conn.close()

    return df


# -----------------------------------------------------
# Valuation
# -----------------------------------------------------

@st.cache_data(ttl=600)
def get_valuation(ticker):

    conn = get_connection()

    query = """
    SELECT *
    FROM valuation_summary
    WHERE company_id = ?
    """

    try:

        df = pd.read_sql(
            query,
            conn,
            params=(ticker,)
        )

    except Exception:

        df = pd.DataFrame()

    conn.close()

    return df