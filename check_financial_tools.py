from financial_tools import (
    calculate_operating_margin,
    calculate_revenue_growth,
)


# Fikcyjne dane do sprawdzenia działania funkcji.
previous_revenue = 1_000_000
current_revenue = 1_200_000
operating_profit = -60_000

margin = calculate_operating_margin(
    revenue=current_revenue,
    operating_profit=operating_profit,
)

growth = calculate_revenue_growth(
    previous_revenue=previous_revenue,
    current_revenue=current_revenue,
)

print(f"Marża operacyjna: {margin:.2f}%")
print(f"Dynamika przychodów: {growth:.2f}%")

# Sprawdzamy, czy program wykrywa nieprawidłowe dane.
try:
    calculate_operating_margin(
        revenue=0,
        operating_profit=100,
    )
except ValueError as error:
    print(f"Kontrolowany błąd: {error}")