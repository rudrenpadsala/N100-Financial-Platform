import sqlite3
import yaml
import pandas as pd

DB_PATH = "db/nifty100.db"
CONFIG_PATH = "src/config/screener_config.yaml"


def load_data():
    """
    Load financial ratios and company data.
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
    Apply screener filters.
    """

    filtered = df.copy()

    # ----------------------------------
    # ROE
    # ----------------------------------

    if "roe_min" in filters:
        filtered = filtered[
            filtered["return_on_equity_pct"] >=
            filters["roe_min"]
        ]

    # ----------------------------------
    # Debt to Equity
    # Skip Financial Sector
    # ----------------------------------

    if "de_max" in filters:

        if "broad_sector" in filtered.columns:

            financials = filtered[
                filtered["broad_sector"] == "Financials"
            ]

            others = filtered[
                filtered["broad_sector"] != "Financials"
            ]

            others = others[
                (
                    others["debt_to_equity"].isna()
                )
                |
                (
                    others["debt_to_equity"] <=
                    filters["de_max"]
                )
            ]

            filtered = pd.concat(
                [financials, others],
                ignore_index=True
            )

        else:

            filtered = filtered[
                (
                    filtered["debt_to_equity"].isna()
                )
                |
                (
                    filtered["debt_to_equity"] <=
                    filters["de_max"]
                )
            ]

    # ----------------------------------
    # Free Cash Flow
    # ----------------------------------

    if "fcf_min" in filters:

        filtered = filtered[
            filtered["free_cash_flow_cr"] >=
            filters["fcf_min"]
        ]

    # ----------------------------------
    # Revenue CAGR
    # ----------------------------------

    if "revenue_cagr_min" in filters:

        filtered = filtered[
            filtered["revenue_cagr_5yr"] >=
            filters["revenue_cagr_min"]
        ]

    # ----------------------------------
    # PAT CAGR
    # ----------------------------------

    if "pat_cagr_min" in filters:

        filtered = filtered[
            filtered["pat_cagr_5yr"] >=
            filters["pat_cagr_min"]
        ]

    # ----------------------------------
    # Operating Margin
    # ----------------------------------

    if "opm_min" in filters:

        filtered = filtered[
            filtered["operating_profit_margin_pct"] >=
            filters["opm_min"]
        ]

    # ----------------------------------
    # ICR
    # Debt Free always passes
    # ----------------------------------

    if "icr_min" in filters:

        if "icr_label" in filtered.columns:

            filtered = filtered[
                (
                    filtered["icr_label"] == "Debt Free"
                )
                |
                (
                    filtered["interest_coverage"] >=
                    filters["icr_min"]
                )
            ]

        else:

            filtered = filtered[
                filtered["interest_coverage"] >=
                filters["icr_min"]
            ]

    # ----------------------------------
    # PE
    # ----------------------------------

    if (
        "pe_max" in filters
        and "price_to_earnings" in filtered.columns
    ):

        filtered = filtered[
            filtered["price_to_earnings"] <=
            filters["pe_max"]
        ]

    # ----------------------------------
    # PB
    # ----------------------------------

    if (
        "pb_max" in filters
        and "price_to_book" in filtered.columns
    ):

        filtered = filtered[
            filtered["price_to_book"] <=
            filters["pb_max"]
        ]

    # ----------------------------------
    # Dividend Yield
    # ----------------------------------

    if (
        "dividend_yield_min" in filters
        and "dividend_yield" in filtered.columns
    ):

        filtered = filtered[
            filtered["dividend_yield"] >=
            filters["dividend_yield_min"]
        ]

    # ----------------------------------
    # Dividend Payout
    # ----------------------------------

    if "dividend_payout_max" in filters:

        filtered = filtered[
            filtered["dividend_payout_ratio_pct"] <=
            filters["dividend_payout_max"]
        ]

    # ----------------------------------
    # Sales
    # ----------------------------------

    if (
        "sales_min" in filters
        and "sales" in filtered.columns
    ):

        filtered = filtered[
            filtered["sales"] >=
            filters["sales_min"]
        ]

    return filtered

def run_screener(filters):
    """
    Run screener.
    """

    ratios, companies = load_data()

    df = ratios.merge(
        companies,
        left_on="company_id",
        right_on="id",
        how="left"
    )

    # ----------------------------------
    # Keep Latest Year Only
    # ----------------------------------

    if "year" in df.columns:

        df = (
            df
            .sort_values("year")
            .groupby("company_id")
            .tail(1)
        )

    # ----------------------------------
    # Apply Filters
    # ----------------------------------

    df = apply_filters(
        df,
        filters
    )

    # ----------------------------------
    # Sort by Composite Score
    # ----------------------------------

    if "composite_quality_score" in df.columns:

        df = df.sort_values(
            by="composite_quality_score",
            ascending=False
        )

    df = df.reset_index(drop=True)

    return df

def run_all_presets():
    """
    Run all screener presets.
    """

    config = load_config()

    results = {}

    print("\n" + "=" * 60)
    print("Running All Screener Presets")
    print("=" * 60)

    for preset_name, filters in config.items():

        print("\n" + "-" * 60)
        print(f"Preset : {preset_name}")
        print("-" * 60)

        df = run_screener(filters)

        print(f"Companies Found : {len(df)}")

        results[preset_name] = df

    print("\n" + "=" * 60)
    print("All Presets Completed")
    print("=" * 60)

    return results

def main():
    """
    Run Financial Screener.
    """

    print("=" * 60)
    print("Financial Screener")
    print("=" * 60)

    all_results = run_all_presets()

    for preset_name, df in all_results.items():

        print("\n" + "=" * 60)
        print(f"PRESET : {preset_name}")
        print("=" * 60)

        print(f"Companies Found : {len(df)}")

        if len(df) == 0:
            print("No companies found.")
            continue

        columns = [
            "company_id",
            "year",
            "return_on_equity_pct",
            "debt_to_equity",
            "free_cash_flow_cr",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "composite_quality_score"
        ]

        columns = [
            c for c in columns
            if c in df.columns
        ]

        print("\nTop Results:\n")

        print(
            df[columns].head(10)
        )

    print("\n" + "=" * 60)
    print("Financial Screener Completed Successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()
