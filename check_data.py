from database import get_financial_data
from financial_tools import (
    calculate_operating_margin,
    calculate_revenue_growth,
)


previous = get_financial_data("DemoCo", 2023)
current = get_financial_data("DemoCo", 2024)

# Przed porównaniem sprawdzamy walutę i jednostkę danych.
if (
    previous["currency"] != current["currency"]
    or previous["unit"] != current["unit"]
):
    raise ValueError("Dane mają różne waluty lub jednostki.")

margin = calculate_operating_margin(
    revenue=current["revenue"],
    operating_profit=current["operating_profit"],
)

growth = calculate_revenue_growth(
    previous_revenue=previous["revenue"],
    current_revenue=current["revenue"],
)

print(f"Spółka: {current['company']}")
print(f"Rok: {current['year']}")
print(f"Marża operacyjna: {margin:.2f}%")
print(f"Dynamika przychodów r/r: {growth:.2f}%")
print(f"Źródło: {current['source']}")

# Sprawdzamy zachowanie przy braku danych.
try:
    get_financial_data("DemoCo", 2025)
except ValueError as error:
    print(f"Kontrolowany błąd: {error}")