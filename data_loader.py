import csv
from pathlib import Path


DATA_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "financials.csv"
)


def load_financial_data():
    """Wczytuje dane finansowe z naszego pliku CSV."""
    if not DATA_PATH.is_file():
        raise FileNotFoundError(
            f"Nie znaleziono pliku: {DATA_PATH}"
        )

    records = []
    seen = set()

    with DATA_PATH.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        required_columns = {
            "company",
            "year",
            "revenue",
            "operating_profit",
            "currency",
            "unit",
            "source",
        }

        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError("W pliku CSV brakuje wymaganych kolumn.")

        for row in reader:
            record = {
                "company": row["company"].strip(),
                "year": int(row["year"]),
                "revenue": float(row["revenue"]),
                "operating_profit": float(row["operating_profit"]),
                "currency": row["currency"].strip(),
                "unit": int(row["unit"]),
                "source": row["source"].strip(),
            }

            key = (record["company"].casefold(), record["year"])

            if key in seen:
                raise ValueError(
                    f"Powtórzone dane: {record['company']}, "
                    f"rok {record['year']}."
                )

            seen.add(key)
            records.append(record)

    if not records:
        raise ValueError("Plik CSV nie zawiera danych.")

    return records


def get_financial_data(company, year):
    """Zwraca dane jednej spółki dla wskazanego roku."""
    records = load_financial_data()

    for record in records:
        same_company = (
            record["company"].casefold()
            == company.strip().casefold()
        )

        if same_company and record["year"] == year:
            return record

    raise ValueError(
        f"Brak danych dla spółki {company} za rok {year}."
    )