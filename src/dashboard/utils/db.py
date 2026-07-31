"""
Shared SQLite Data Loader
Used by every Streamlit screen
"""

import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "db/nifty100.db"


# -----------------------------------------------------
# SQLite Connection
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
def get_ratios(ticker=None, year=None):

    conn = get_connection()

    query = """
    SELECT *
    FROM financial_ratios
    """

    conditions = []
    params = []

    if ticker is not None:
        conditions.append("company_id = ?")
        params.append(ticker)

    if year is not None:
        conditions.append("year = ?")
        params.append(year)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY company_id, year"

    df = pd.read_sql(
        query,
        conn,
        params=params
    )

    conn.close()

    return df


# -----------------------------------------------------
# Profit & Loss
# -----------------------------------------------------

@st.cache_data(ttl=600)
def get_pl(ticker=None):

    conn = get_connection()

    query = """
    SELECT *
    FROM profitandloss
    """

    params = []

    if ticker is not None:
        query += " WHERE company_id = ?"
        params.append(ticker)

    query += " ORDER BY year"

    df = pd.read_sql(
        query,
        conn,
        params=params,
    )

    conn.close()

    return df


# -----------------------------------------------------
# Balance Sheet
# -----------------------------------------------------

@st.cache_data(ttl=600)
def get_bs(ticker=None):

    conn = get_connection()

    query = """
    SELECT *
    FROM balancesheet
    """

    params = []

    if ticker is not None:
        query += " WHERE company_id = ?"
        params.append(ticker)

    query += " ORDER BY year"

    df = pd.read_sql(
        query,
        conn,
        params=params,
    )

    conn.close()

    return df


# -----------------------------------------------------
# Cash Flow
# -----------------------------------------------------

@st.cache_data(ttl=600)
def get_cf(ticker=None):

    conn = get_connection()

    query = """
    SELECT *
    FROM cashflow
    """

    params = []

    if ticker is not None:
        query += " WHERE company_id = ?"
        params.append(ticker)

    query += " ORDER BY year"

    df = pd.read_sql(
        query,
        conn,
        params=params,
    )

    conn.close()

    return df

# -----------------------------------------------------
# Sector Information
# -----------------------------------------------------

@st.cache_data(ttl=600)
def get_sectors():

    conn = get_connection()

    query = """
    SELECT *
    FROM sectors
    ORDER BY broad_sector, sub_sector
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# -----------------------------------------------------
# Peer Groups
# -----------------------------------------------------

@st.cache_data(ttl=600)
def get_peers(group_name=None):

    conn = get_connection()

    query = """
    SELECT *
    FROM peer_groups
    """

    params = []

    if group_name is not None:
        query += " WHERE peer_group_name = ?"
        params.append(group_name)

    query += """
    ORDER BY
        peer_group_name,
        is_benchmark DESC,
        company_id
    """

    df = pd.read_sql(
        query,
        conn,
        params=params,
    )

    conn.close()

    return df


# -----------------------------------------------------
# Valuation
# -----------------------------------------------------

@st.cache_data(ttl=600)
def get_valuation(ticker=None):

    conn = get_connection()

    try:

        query = """
        SELECT *
        FROM valuation_summary
        """

        params = []

        if ticker is not None:
            query += " WHERE company_id = ?"
            params.append(ticker)

        df = pd.read_sql(
            query,
            conn,
            params=params,
        )

    except Exception:

        # Day 23: valuation table may not exist yet.
        # Day 26 will generate it.
        df = pd.DataFrame()

    conn.close()

    return df