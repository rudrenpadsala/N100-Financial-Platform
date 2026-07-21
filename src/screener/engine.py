import sqlite3
import yaml
import pandas as pd

DB_PATH = "db/nifty100.db"
CONFIG_PATH = "src/config/screener_config.yaml"


def load_data():
    """
    Load financial ratios and company master data.
    """

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    companies = pd.read_sql(
        "SELECT * FROM companies",
        conn
    )

    conn.close()

    return ratios, companies


def load_config():
    """
    Load screener configuration.
    """

    with open(CONFIG_PATH, "r") as file:
        config = yaml.safe_load(file)

    return config

def apply_filters(df, filters):
    """
    Apply screener filters to the financial ratios DataFrame.
    """

    filtered = df.copy()

    # ----------------------------------
    # ROE Minimum
    # ----------------------------------

    if "roe_min" in filters:
        filtered = filtered[
            filtered["return_on_equity_pct"] >= filters["roe_min"]
        ]

    # ----------------------------------
    # Debt to Equity Maximum
    # ----------------------------------

    if "de_max" in filters:
        filtered = filtered[
            (
                filtered["debt_to_equity"].isna()
            )
            |
            (
                filtered["debt_to_equity"] <= filters["de_max"]
            )
        ]

    # ----------------------------------
    # Free Cash Flow Minimum
    # ----------------------------------

    if "fcf_min" in filters:
        filtered = filtered[
            filtered["free_cash_flow_cr"] >= filters["fcf_min"]
        ]

    # ----------------------------------
    # Revenue CAGR Minimum
    # ----------------------------------

    if "revenue_cagr_min" in filters:
        filtered = filtered[
            filtered["revenue_cagr_5yr"] >= filters["revenue_cagr_min"]
        ]

    # ----------------------------------
    # PAT CAGR Minimum
    # ----------------------------------

    if "pat_cagr_min" in filters:
        filtered = filtered[
            filtered["pat_cagr_5yr"] >= filters["pat_cagr_min"]
        ]

    # ----------------------------------
    # Operating Profit Margin Minimum
    # ----------------------------------

    if "opm_min" in filters:
        filtered = filtered[
            filtered["operating_profit_margin_pct"] >= filters["opm_min"]
        ]

    return filtered

def run_screener(filters):
    """
    Run screener using supplied filters.
    """

    ratios, companies = load_data()

    # Merge company information
    df = ratios.merge(
        companies,
        left_on="company_id",
        right_on="id",
        how="left"
    )

    # Apply filters
    df = apply_filters(df, filters)

    # Sort by composite score
    if "composite_quality_score" in df.columns:
        df = df.sort_values(
            by="composite_quality_score",
            ascending=False
        )

    return df


def main():

    print("=" * 60)
    print("Financial Screener")
    print("=" * 60)

    config = load_config()

    for preset_name, filters in config.items():

        print("\n" + "=" * 60)
        print("Preset :", preset_name)
        print("=" * 60)

        result = run_screener(filters)

        print("Companies :", len(result))

        if len(result):

            cols = [
                "company_id",
                "year",
                "return_on_equity_pct",
                "debt_to_equity",
                "free_cash_flow_cr",
                "revenue_cagr_5yr",
                "composite_quality_score"
            ]

            cols = [
                c for c in cols
                if c in result.columns
            ]

            print(result[cols].head(5))

        else:
            print("No matching companies.")

if __name__ == "__main__":
    main()


