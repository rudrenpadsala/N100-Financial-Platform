"""
loader.py

Load all Excel files from data/raw.
"""

from pathlib import Path
import pandas as pd

# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_PATH = BASE_DIR / "data" / "raw"

# Files where the actual header starts from the second row
HEADER_ONE_FILES = {
    "analysis",
    "balancesheet",
    "cashflow",
    "companies",
    "documents",
    "profitandloss",
    "prosandcons",
}


# ==========================================================
# Load All Excel Files
# ==========================================================

def load_all_excel_files():

    datasets = {}

    excel_files = sorted(RAW_DATA_PATH.glob("*.xlsx"))

    print("=" * 70)
    print("Loading Excel Files")
    print("=" * 70)

    for file in excel_files:

        try:

            if file.stem in HEADER_ONE_FILES:
                df = pd.read_excel(file, header=1)
            else:
                df = pd.read_excel(file)

            # Remove completely empty rows
            df = df.dropna(how="all")

            # Remove completely empty columns
            df = df.dropna(axis=1, how="all")

            # Remove duplicate rows
            df = df.drop_duplicates()

            # Clean column names
            df.columns = (
                df.columns.astype(str)
                .str.strip()
                .str.replace("\n", " ", regex=False)
                .str.replace("  ", " ", regex=False)
            )

            datasets[file.stem] = df

            print(f"✔ Loaded : {file.name}")

        except Exception as e:

            print(f"❌ Error : {file.name}")
            print(e)

    return datasets


# ==========================================================
# Get One Dataset
# ==========================================================

def get_dataset(dataset_name):

    datasets = load_all_excel_files()

    if dataset_name not in datasets:
        raise ValueError(f"{dataset_name} not found.")

    return datasets[dataset_name]


# ==========================================================
# Dataset Summary
# ==========================================================

def show_summary(datasets):

    print("\n")
    print("=" * 70)
    print("Dataset Summary")
    print("=" * 70)

    for name, df in datasets.items():

        print(f"\n{name}")

        print("-" * 70)

        print(f"Rows    : {df.shape[0]}")
        print(f"Columns : {df.shape[1]}")

        print("\nColumn Names")

        for col in df.columns:
            print(f"• {col}")

        print("-" * 70)

    print(f"\nTotal Datasets Loaded : {len(datasets)}")


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    datasets = load_all_excel_files()

    show_summary(datasets)