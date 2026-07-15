import pandas as pd

from src.etl.normaliser import (
    normalize_year,
    normalize_ticker
)


def test_normalize_year_1():

    df = pd.DataFrame({"year": ["FY2022"]})

    df = normalize_year(df)

    assert df["year"][0] == 2022


def test_normalize_year_2():

    df = pd.DataFrame({"year": ["2023"]})

    df = normalize_year(df)

    assert df["year"][0] == 2023


def test_normalize_year_3():

    df = pd.DataFrame({"year": ["2024*"]})

    df = normalize_year(df)

    assert df["year"][0] == 2024


def test_normalize_year_4():

    df = pd.DataFrame({"year": [None]})

    df = normalize_year(df)

    assert pd.isna(df["year"][0])


def test_normalize_year_5():

    df = pd.DataFrame({"year": ["abcd"]})

    df = normalize_year(df)

    assert pd.isna(df["year"][0])


def test_ticker_uppercase():

    df = pd.DataFrame({

        "ticker": [

            "tcs",
            "infy"

        ]

    })

    df = normalize_ticker(df)

    assert df["ticker"].tolist() == [

        "TCS",
        "INFY"

    ]


def test_ticker_spaces():

    df = pd.DataFrame({

        "ticker": [

            " tcs ",
            " reliance "

        ]

    })

    df = normalize_ticker(df)

    assert df["ticker"].tolist() == [

        "TCS",
        "RELIANCE"

    ]


def test_symbol_column():

    df = pd.DataFrame({

        "symbol": [

            "hdfc",
            "icici"

        ]

    })

    df = normalize_ticker(df)

    assert df["symbol"].tolist() == [

        "HDFC",
        "ICICI"

    ]