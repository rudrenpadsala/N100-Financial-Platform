"""
cashflow_kpis.py

Sprint 2
Day 11

Cash Flow KPI Engine
"""


# --------------------------------------------------
# Free Cash Flow
# --------------------------------------------------

def free_cash_flow(
    operating_activity,
    investing_activity
):
    """
    Free Cash Flow

    Formula:
        Operating Activity + Investing Activity

    Note:
        Investing Activity is usually negative.
        Negative FCF is allowed.
    """

    if operating_activity is None:
        return None

    if investing_activity is None:
        return None

    return round(
        operating_activity +
        investing_activity,
        2
    )

# --------------------------------------------------
# FCF Conversion
# --------------------------------------------------

def fcf_conversion_rate(
    free_cashflow,
    operating_profit
):
    """
    Formula:

    FCF / Operating Profit ×100
    """

    if operating_profit is None:
        return None

    if operating_profit == 0:
        return None

    return round(
        (free_cashflow / operating_profit) * 100,
        2
    )


# --------------------------------------------------
# CFO Quality Score
# --------------------------------------------------

def cfo_quality_score(
    cash_from_operations,
    net_profit
):
    """
    CFO Quality Score

    Formula:
        CFO / PAT

    Rules:
        > 1.0  -> High Quality
        0.5-1.0 -> Moderate
        < 0.5 -> Accrual Risk
        PAT = 0 -> None
    """

    if net_profit is None:
        return None, None

    if net_profit == 0:
        return None, None

    score = cash_from_operations / net_profit

    if score > 1:
        label = "High Quality"

    elif score >= 0.5:
        label = "Moderate"

    else:
        label = "Accrual Risk"

    return round(score, 2), label


# --------------------------------------------------
# CapEx Intensity
# --------------------------------------------------

def capex_intensity(
    investing_activity,
    sales
):
    """
    CapEx Intensity

    Formula:
        abs(Investing Activity) / Sales ×100
    """

    if sales is None:
        return None, None

    if sales == 0:
        return None, None

    intensity = (
        abs(investing_activity) / sales
    ) * 100

    if intensity < 3:
        label = "Asset Light"

    elif intensity <= 8:
        label = "Moderate"

    else:
        label = "Capital Intensive"

    return round(intensity, 2), label


# --------------------------------------------------
# Capital Allocation Pattern
# --------------------------------------------------

def capital_allocation_pattern(
    operating_activity,
    investing_activity,
    financing_activity
):
    """
    Capital Allocation Pattern

    Returns:
        cfo_sign,
        cfi_sign,
        cff_sign,
        pattern_label
    """

    cfo_sign = "+" if operating_activity >= 0 else "-"
    cfi_sign = "+" if investing_activity >= 0 else "-"
    cff_sign = "+" if financing_activity >= 0 else "-"

    pattern = (cfo_sign, cfi_sign, cff_sign)

    patterns = {
        ("+", "-", "-"): "Reinvestor",
        ("+", "+", "-"): "Liquidating Assets",
        ("-", "+", "+"): "Distress Signal",
        ("-", "-", "+"): "Growth Funded by Debt",
        ("+", "+", "+"): "Cash Accumulator",
        ("-", "-", "-"): "Pre-Revenue",
        ("+", "-", "+"): "Mixed"
    }

    label = patterns.get(pattern, "Unknown")

    return (
        cfo_sign,
        cfi_sign,
        cff_sign,
        label
    )


