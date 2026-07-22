import sqlite3
import yaml
import pandas as pd

from openpyxl import load_workbook
from openpyxl.styles import PatternFill

from src.screener.exporter import export_presets

DB_PATH = "db/nifty100.db"
CONFIG_PATH = "src/config/screener_config.yaml"
OUTPUT_FILE = "output/screener_output.xlsx"


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
    Apply screener filters.
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
                    others["debt_to_equity"] <= filters["de_max"]
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
                    filtered["debt_to_equity"] <= filters["de_max"]
                )
            ]

    # ----------------------------------
    # Free Cash Flow
    # ----------------------------------

    if "fcf_min" in filters:

        filtered = filtered[
            filtered["free_cash_flow_cr"] >= filters["fcf_min"]
        ]

    # ----------------------------------
    # Revenue CAGR (5 Year)
    # ----------------------------------

    if "revenue_cagr_min" in filters:

        filtered = filtered[
            filtered["revenue_cagr_5yr"] >=
            filters["revenue_cagr_min"]
        ]

    # ----------------------------------
    # PAT CAGR (5 Year)
    # ----------------------------------

    if "pat_cagr_min" in filters:

        filtered = filtered[
            filtered["pat_cagr_5yr"] >=
            filters["pat_cagr_min"]
        ]

    # ----------------------------------
    # Operating Profit Margin
    # ----------------------------------

    if "opm_min" in filters:

        filtered = filtered[
            filtered["operating_profit_margin_pct"] >=
            filters["opm_min"]
        ]

    # ----------------------------------
    # Interest Coverage Ratio
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
    # Price to Earnings
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
    # Price to Book
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
    # Market Cap
    # ----------------------------------

    if (
        "market_cap_min" in filters
        and "market_cap" in filtered.columns
    ):

        filtered = filtered[
            filtered["market_cap"] >=
            filters["market_cap_min"]
        ]

    # ----------------------------------
    # Net Profit
    # ----------------------------------

    if (
        "net_profit_min" in filters
        and "net_profit" in filtered.columns
    ):

        filtered = filtered[
            filtered["net_profit"] >=
            filters["net_profit_min"]
        ]

    # ----------------------------------
    # EPS CAGR
    # ----------------------------------

    if (
        "eps_cagr_min" in filters
        and "eps_cagr_5yr" in filtered.columns
    ):

        filtered = filtered[
            filtered["eps_cagr_5yr"] >=
            filters["eps_cagr_min"]
        ]

    # ----------------------------------
    # Asset Turnover
    # ----------------------------------

    if (
        "asset_turnover_min" in filters
        and "asset_turnover" in filtered.columns
    ):

        filtered = filtered[
            filtered["asset_turnover"] >=
            filters["asset_turnover_min"]
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
    Run screener using supplied filters.
    """

    ratios, companies = load_data()

    # ----------------------------------
    # Merge Company Master
    # ----------------------------------

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
            .groupby("company_id", as_index=False)
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
    # Composite Score
    # ----------------------------------

    df = calculate_composite_score(df)

    # ----------------------------------
    # Sort by Composite Score
    # ----------------------------------

    if "composite_quality_score" in df.columns:

        df = df.sort_values(
            by="composite_quality_score",
            ascending=False
        )

    # ----------------------------------
    # Reset Index
    # ----------------------------------

    df = df.reset_index(
        drop=True
    )

    return df

def winsorize_and_scale(series):
    """
    Winsorize using P10/P90 and scale to 0-100.
    """

    s = series.copy().fillna(0)

    p10 = s.quantile(0.10)
    p90 = s.quantile(0.90)

    s = s.clip(lower=p10, upper=p90)

    if p90 == p10:
        return pd.Series(50, index=s.index)

    return ((s - p10) / (p90 - p10)) * 100

def calculate_composite_score(df):
    """
    Calculate composite quality score.

    Weightage
    ----------
    Profitability : 35%
    Cash Quality  : 30%
    Growth        : 20%
    Leverage      : 15%

    Also computes sector-relative score.
    """

    import numpy as np

    df = df.copy()

    score = pd.Series(0.0, index=df.index)

    # -------------------------------------------------------
    # Profitability (35%)
    # -------------------------------------------------------

    if "return_on_equity_pct" in df.columns:
        roe = winsorize_and_scale(df["return_on_equity_pct"])
        score += roe * 0.15

    if "return_on_capital_employed_pct" in df.columns:
        roce = winsorize_and_scale(
            df["return_on_capital_employed_pct"]
        )
        score += roce * 0.10

    if "net_profit_margin_pct" in df.columns:
        npm = winsorize_and_scale(
            df["net_profit_margin_pct"]
        )
        score += npm * 0.10

    # -------------------------------------------------------
    # Cash Quality (30%)
    # -------------------------------------------------------

    if "fcf_cagr_5yr" in df.columns:
        fcf = winsorize_and_scale(
            df["fcf_cagr_5yr"]
        )
        score += fcf * 0.15

    if "cfo_quality_score" in df.columns:
        cfo = winsorize_and_scale(
            df["cfo_quality_score"]
        )
        score += cfo * 0.10

    if "free_cash_flow_cr" in df.columns:

        score += (
            (df["free_cash_flow_cr"] > 0)
            .astype(float)
            * 5
        )

    # -------------------------------------------------------
    # Growth (20%)
    # -------------------------------------------------------

    if "revenue_cagr_5yr" in df.columns:
        revenue = winsorize_and_scale(
            df["revenue_cagr_5yr"]
        )
        score += revenue * 0.10

    if "pat_cagr_5yr" in df.columns:
        pat = winsorize_and_scale(
            df["pat_cagr_5yr"]
        )
        score += pat * 0.10

    # -------------------------------------------------------
    # Leverage (15%)
    # -------------------------------------------------------

    if "debt_to_equity" in df.columns:
        de = winsorize_and_scale(
            -df["debt_to_equity"].fillna(0)
        )
        score += de * 0.10

    if "interest_coverage" in df.columns:
        icr = winsorize_and_scale(
            df["interest_coverage"]
        )
        score += icr * 0.05

    # -------------------------------------------------------
    # Final Score
    # -------------------------------------------------------

    score = score.fillna(0)

    if score.max() > score.min():

        score = (
            (score - score.min())
            / (score.max() - score.min())
        ) * 100

    else:

        score = pd.Series(
            50,
            index=score.index
        )

    df["composite_quality_score"] = score.round(2)

    # -------------------------------------------------------
    # Sector Relative Score
    # -------------------------------------------------------

    if "broad_sector" in df.columns:

        df["sector_relative_score"] = (
            df.groupby("broad_sector")[
                "composite_quality_score"
            ]
            .transform(
                lambda x: (
                    (
                        x - x.min()
                    )
                    /
                    (
                        x.max() - x.min()
                    )
                    * 100
                )
                if x.max() != x.min()
                else 50
            )
            .round(2)
        )

    else:

        df["sector_relative_score"] = (
            df["composite_quality_score"]
        )

    return df


def calculate_sector_relative_score(df):
    """
    Calculate sector-relative composite score.
    """

    if "broad_sector" not in df.columns:
        return df

    df["sector_relative_score"] = (
        df.groupby("broad_sector")["composite_quality_score"]
        .transform(
            lambda x: (
                (x - x.min()) /
                (x.max() - x.min())
                if x.max() != x.min()
                else 1
            ) * 100
        )
    ).round(2)

    return df


def export_presets(results):
    """
    Export every screener preset to Excel.
    """

    from pathlib import Path

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "screener_output.xlsx"

    with pd.ExcelWriter(
        output_file,
        engine="openpyxl"
    ) as writer:

        for preset_name, df in results.items():

            export_df = df.copy()

            export_columns = [

                "company_id",
                "company_name",
                "broad_sector",
                "year",

                "return_on_equity_pct",
                "return_on_capital_employed_pct",
                "net_profit_margin_pct",

                "free_cash_flow_cr",
                "fcf_cagr_5yr",
                "cfo_quality_score",

                "revenue_cagr_5yr",
                "pat_cagr_5yr",

                "debt_to_equity",
                "interest_coverage",

                "price_to_earnings",
                "price_to_book",

                "dividend_yield",
                "dividend_payout_ratio_pct",

                "sales",

                "composite_quality_score",
                "sector_relative_score"
]

            export_columns = [
                c for c in export_columns
                if c in export_df.columns
            ]

            export_df = (
                export_df[export_columns]
                .sort_values(
                    "composite_quality_score",
                    ascending=False
                )
            )

            export_df.to_excel(
                writer,
                sheet_name=preset_name[:31],
                index=False
            )

    print("\nExcel saved :", output_file)


def format_excel():
    """
    Apply conditional formatting to screener output.
    """

    workbook = load_workbook("output/screener_output.xlsx")

    green = PatternFill(
        fill_type="solid",
        start_color="C6EFCE",
        end_color="C6EFCE"
    )

    red = PatternFill(
        fill_type="solid",
        start_color="FFC7CE",
        end_color="FFC7CE"
    )

    threshold_map = {
        "return_on_equity_pct": 15,
        "return_on_capital_employed_pct": 15,
        "revenue_cagr_5yr": 10,
        "pat_cagr_5yr": 10,
        "debt_to_equity": 1,
        "interest_coverage": 3
    }

    for sheet in workbook.sheetnames:

        ws = workbook[sheet]

        headers = {
            cell.value: cell.column
            for cell in ws[1]
        }

        for metric, threshold in threshold_map.items():

            if metric not in headers:
                continue

            col = headers[metric]

            for row in range(2, ws.max_row + 1):

                cell = ws.cell(row=row, column=col)

                if cell.value is None:
                    continue

                if metric == "debt_to_equity":

                    if cell.value <= threshold:
                        cell.fill = green
                    else:
                        cell.fill = red

                else:

                    if cell.value >= threshold:
                        cell.fill = green
                    else:
                        cell.fill = red

    workbook.save("output/screener_output.xlsx")

    print("Excel formatting applied.")

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

        # ----------------------------------
        # Run Screener
        # ----------------------------------

        df = run_screener(filters)

        # ----------------------------------
        # Calculate Composite Score
        # ----------------------------------

        df = calculate_composite_score(df)

        # ----------------------------------
        # Calculate Sector Relative Score
        # ----------------------------------

        df = calculate_sector_relative_score(df)

        print(f"Companies Found : {len(df)}")

        results[preset_name] = df

    # ----------------------------------
    # Export Excel Workbook
    # ----------------------------------

    export_presets(results)

    # ----------------------------------
    # Apply Excel Formatting
    # ----------------------------------

    format_excel()

    print("\n" + "=" * 60)
    print("Excel Export Completed")
    print("=" * 60)

    return results

def main():
    """
    Main entry point.
    """

    print("=" * 60)
    print("Financial Screener")
    print("=" * 60)

    all_results = run_all_presets()

    for preset, df in all_results.items():

        print("\n" + "=" * 60)
        print(f"PRESET : {preset}")
        print("=" * 60)

        print(f"Companies Found : {len(df)}")

        if len(df) == 0:
            print("No companies found.")
            continue

        cols = [
            "company_id",
            "company_name",
            "broad_sector",
            "year",
            "return_on_equity_pct",
            "return_on_capital_employed_pct",
            "net_profit_margin_pct",
            "free_cash_flow_cr",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "debt_to_equity",
            "interest_coverage",
            "composite_quality_score",
            "sector_relative_score"
        ]

        cols = [c for c in cols if c in df.columns]

        print("\nTop Results:\n")

        print(
            df[cols]
            .head(10)
            .to_string(index=False)
        )

    print("\n" + "=" * 60)
    print("Financial Screener Completed Successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()




