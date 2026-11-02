import sqlite3
from pathlib import Path

from data_loader import load_financial_data


DB_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "financials.db"
)


def setup_database():
    # Korzystamy z istniejącego odczytu i sprawdzania CSV.
    records = load_financial_data()

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    try:
        # Zmiany danych zatwierdzamy razem.
        # Przy błędzie operacje w transakcji zostaną cofnięte.
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS financials (
                    company TEXT NOT NULL COLLATE NOCASE,
                    year INTEGER NOT NULL,
                    revenue REAL NOT NULL CHECK (revenue >= 0),
                    operating_profit REAL NOT NULL,
                    currency TEXT NOT NULL,
                    unit INTEGER NOT NULL CHECK (unit > 0),
                    source TEXT NOT NULL,
                    PRIMARY KEY (company, year)
                )
            """)

            connection.executemany("""
                INSERT INTO financials (
                    company,
                    year,
                    revenue,
                    operating_profit,
                    currency,
                    unit,
                    source
                )
                VALUES (
                    :company,
                    :year,
                    :revenue,
                    :operating_profit,
                    :currency,
                    :unit,
                    :source
                )
                ON CONFLICT(company, year) DO UPDATE SET
                    revenue = excluded.revenue,
                    operating_profit = excluded.operating_profit,
                    currency = excluded.currency,
                    unit = excluded.unit,
                    source = excluded.source
            """, records)

        rows = connection.execute("""
            SELECT company, year, revenue, operating_profit
            FROM financials
            ORDER BY company, year
        """).fetchall()

        print(f"Baza danych: {DB_PATH}")
        print(f"Liczba rekordów w bazie: {len(rows)}")

        for company, year, revenue, operating_profit in rows:
            print(
                f"{company} | {year} | "
                f"przychody: {revenue:.2f} | "
                f"wynik operacyjny: {operating_profit:.2f}"
            )

    finally:
        connection.close()


if __name__ == "__main__":
    setup_database()