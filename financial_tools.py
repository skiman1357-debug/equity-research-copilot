def calculate_operating_margin(revenue, operating_profit):
    """Oblicza marżę operacyjną w procentach."""
    if revenue <= 0:
        raise ValueError("Przychody muszą być większe od zera.")

    return (operating_profit / revenue) * 100


def calculate_revenue_growth(previous_revenue, current_revenue):
    """Oblicza zmianę przychodów w procentach."""
    if previous_revenue <= 0:
        raise ValueError(
            "Przychody poprzedniego okresu muszą być większe od zera."
        )

    if current_revenue < 0:
        raise ValueError("Przychody obecnego okresu nie mogą być ujemne.")

    return (
        (current_revenue - previous_revenue)
        / previous_revenue
    ) * 100