import pytest

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    opm_cross_check,
    return_on_equity,
    return_on_capital_employed,
    roce_benchmark,
    return_on_assets
)


# --------------------------------------------------
# Test 1
# Net Profit Margin - Normal Case
# --------------------------------------------------

def test_net_profit_margin():

    assert net_profit_margin(200, 1000) == 20.0


# --------------------------------------------------
# Test 2
# Net Profit Margin - Sales = 0
# --------------------------------------------------

def test_net_profit_margin_zero_sales():

    assert net_profit_margin(200, 0) is None


# --------------------------------------------------
# Test 3
# Operating Profit Margin
# --------------------------------------------------

def test_operating_profit_margin():

    assert operating_profit_margin(300, 1000) == 30.0


# --------------------------------------------------
# Test 4
# OPM Cross Check
# --------------------------------------------------

def test_opm_cross_check():

    assert opm_cross_check(30, 35) is False


# --------------------------------------------------
# Test 5
# ROE Normal
# --------------------------------------------------

def test_return_on_equity():

    assert return_on_equity(200, 500, 500) == 20.0


# --------------------------------------------------
# Test 6
# ROE Negative Equity
# --------------------------------------------------

def test_return_on_equity_negative():

    assert return_on_equity(100, -100, -50) is None


# --------------------------------------------------
# Test 7
# ROCE
# --------------------------------------------------

def test_return_on_capital_employed():

    assert return_on_capital_employed(
        300,
        500,
        500,
        500
    ) == 20.0


# --------------------------------------------------
# Test 8
# ROA
# --------------------------------------------------

def test_return_on_assets():

    assert return_on_assets(200, 1000) == 20.0