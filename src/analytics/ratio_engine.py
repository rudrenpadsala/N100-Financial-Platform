import sqlite3
import pandas as pd

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    debt_to_equity,
    interest_coverage_ratio,
    asset_turnover
)

from src.analytics.cashflow_kpis import (
    free_cash_flow
)

DB_PATH = "db/nifty100.db"


def main():

    print("=" * 60)
    print("Financial Ratio Engine")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)

    # -----------------------------
    # Load Tables
    # -----------------------------

    profit_loss = pd.read_sql(
        "SELECT * FROM profitandloss",
        conn
    )

    balance_sheet = pd.read_sql(
        "SELECT * FROM balancesheet",
        conn
    )

    cashflow = pd.read_sql(
        "SELECT * FROM cashflow",
        conn
    )

    print("✔ profitandloss :", len(profit_loss))
    print("✔ balancesheet  :", len(balance_sheet))
    print("✔ cashflow      :", len(cashflow))

    # -----------------------------
    # Remove TTM rows
    # -----------------------------

    profit_loss = profit_loss[
        profit_loss["year"] != "TTM"
    ]

    balance_sheet = balance_sheet[
        balance_sheet["year"] != "TTM"
    ]

    cashflow = cashflow[
        cashflow["year"] != "TTM"
    ]

    # -----------------------------
    # Merge
    # -----------------------------

    # ----------------------------------
# Remove Duplicate Company-Year Records
# ----------------------------------

    profit_loss = profit_loss.drop_duplicates(
        subset=["company_id", "year"],
        keep="first"
    )

    balance_sheet = balance_sheet.drop_duplicates(
        subset=["company_id", "year"],
        keep="first"
    )

    cashflow = cashflow.drop_duplicates(
        subset=["company_id", "year"],
        keep="first"
    )

    print("Duplicates removed.")
    print("Profit & Loss :", len(profit_loss))
    print("Balance Sheet :", len(balance_sheet))
    print("Cash Flow     :", len(cashflow))

    df = (
        profit_loss
        .merge(
            balance_sheet,
            on=["company_id", "year"],
            how="inner"
        )
        .merge(
            cashflow,
            on=["company_id", "year"],
            how="inner"
        )
    )

    print("✔ Merged Rows :", len(df))

    results = []
        # -----------------------------
    # Calculate Ratios
    # -----------------------------

    for _, row in df.iterrows():

        npm = net_profit_margin(
            row["net_profit"],
            row["sales"]
        )

        opm = operating_profit_margin(
            row["operating_profit"],
            row["sales"]
        )

        roe = return_on_equity(
            row["net_profit"],
            row["equity_capital"],
            row["reserves"]
        )

        de = debt_to_equity(
            row["borrowings"],
            row["equity_capital"],
            row["reserves"]
        )

        icr = interest_coverage_ratio(
            row["operating_profit"],
            row["other_income"],
            row["interest"]
        )

        turnover = asset_turnover(
            row["sales"],
            row["total_assets"]
        )

        fcf = free_cash_flow(
            row["operating_activity"],
            row["investing_activity"]
        )

        capex = (
            abs(row["investing_activity"])
            if pd.notna(row["investing_activity"])
            else None
        )

        eps = row["eps"]

        if (
            pd.notna(row["equity_capital"])
            and row["equity_capital"] != 0
        ):
            book_value = (
                row["equity_capital"] + row["reserves"]
            ) / row["equity_capital"]
        else:
            book_value = None

        dividend = row["dividend_payout"]

        total_debt = row["borrowings"]

        cfo = row["operating_activity"]



        results.append({

            "company_id": row["company_id"],
            "year": row["year"],

            "net_profit_margin_pct": npm,
            "operating_profit_margin_pct": opm,
            "return_on_equity_pct": roe,
            "debt_to_equity": de,
            "interest_coverage": icr,
            "asset_turnover": turnover,
            "free_cash_flow_cr": fcf,

            "capex_cr": capex,
            "earnings_per_share": eps,
            "book_value_per_share": book_value,
            "dividend_payout_ratio_pct": dividend,
            "total_debt_cr": total_debt,
            "cash_from_operations_cr": cfo

        })

    # ----------------------------------
    # Create DataFrame
    # ----------------------------------

    ratios = pd.DataFrame(results)

    print("\nCalculated Ratio Rows :", len(ratios))

    print("\nPreview:")
    print(ratios.head())

    # ----------------------------------
    # Save to SQLite
    # ----------------------------------

    print("\nSaving ratios to financial_ratios table...")

    # Clear old data
    conn.execute("DELETE FROM financial_ratios")

    # Keep only columns that exist in the table
    ratios = ratios[
        [
            "company_id",
            "year",
            "net_profit_margin_pct",
            "operating_profit_margin_pct",
            "return_on_equity_pct",
            "debt_to_equity",
            "interest_coverage",
            "asset_turnover",
            "free_cash_flow_cr",
            "capex_cr",
            "earnings_per_share",
            "book_value_per_share",
            "dividend_payout_ratio_pct",
            "total_debt_cr",
            "cash_from_operations_cr"
        ]
    ]

    ratios.to_sql(
        "financial_ratios",
        conn,
        if_exists="append",
        index=False
    )

    conn.commit()

    print("✓ financial_ratios table updated successfully.")

    # ----------------------------------
    # Verify Row Count
    # ----------------------------------

    count = pd.read_sql(
        "SELECT COUNT(*) AS total FROM financial_ratios",
        conn
    )

    print("\nRows in financial_ratios:")
    print(count)

    print("\nExpected Rows :", len(ratios))


    # ----------------------------------
    # Close Database
    # ----------------------------------

    conn.close()

    print("\n" + "=" * 60)
    print("Ratio Engine Completed Successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()