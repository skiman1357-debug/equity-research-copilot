import sqlite3
from pathlib import Path


DB_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "financials.db"
)


def get_financial_data(company, year):
    """Pobiera dane spółki za wskazany rok z bazy SQLite."""
    if not DB_PATH.is_file():
        raise FileNotFoundError(
            "Brakuje bazy danych. Uruchom setup_database.py."
        )

    # Otwieramy bazę wyłącznie do odczytu.
    database_uri = DB_PATH.resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(database_uri, uri=True)
    connection.row_factory = sqlite3.Row

    try:
        row = connection.execute(
            """
            SELECT
                company,
                year,
                revenue,
                operating_profit,
                currency,
                unit,
                source
            FROM financials
            WHERE company = ? AND year = ?
            """,
            (company.strip(), year),
        ).fetchone()

    finally:
        connection.close()

    if row is None:
        raise ValueError(
            f"Brak danych dla spółki {company} za rok {year}."
        )

    return dict(row)