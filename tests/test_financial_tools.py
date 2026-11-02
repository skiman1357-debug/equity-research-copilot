import pytest

from financial_tools import (
    calculate_operating_margin,
    calculate_revenue_growth,
)


@pytest.mark.parametrize(
    "revenue, operating_profit, expected",
    [
        (1_200_000, 180_000, 15.0),
        (1_200_000, -60_000, -5.0),
        (1_200_000, 0, 0.0),
    ],
)
def test_operating_margin(revenue, operating_profit, expected):
    result = calculate_operating_margin(revenue, operating_profit)

    assert result == pytest.approx(expected)


@pytest.mark.parametrize("revenue", [0, -100])
def test_margin_rejects_invalid_revenue(revenue):
    with pytest.raises(ValueError):
        calculate_operating_margin(revenue, 100)


@pytest.mark.parametrize(
    "previous, current, expected",
    [
        (1_000_000, 1_200_000, 20.0),
        (1_000_000, 800_000, -20.0),
        (1_000_000, 1_000_000, 0.0),
        (1_000_000, 0, -100.0),
    ],
)
def test_revenue_growth(previous, current, expected):
    result = calculate_revenue_growth(previous, current)

    assert result == pytest.approx(expected)


@pytest.mark.parametrize("previous", [0, -100])
def test_growth_rejects_invalid_base(previous):
    with pytest.raises(ValueError):
        calculate_revenue_growth(previous, 100)


def test_growth_rejects_negative_current_revenue():
    with pytest.raises(ValueError):
        calculate_revenue_growth(100, -50)