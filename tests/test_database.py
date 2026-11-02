import sqlite3

import pytest

import database
import setup_database


@pytest.fixture
def temporary_database(tmp_path, monkeypatch):
    """Tworzy osobną bazę testową, bez zmieniania bazy projektu."""
    db_path = tmp_path / "test_financials.db"

    records = [
        {
            "company": "DemoCo",
            "year": 2024,
            "revenue": 1_350_000,
            "operating_profit": 162_000,
            "currency": "PLN",
            "unit": 1,
            "source": "synthetic_demo",
        }
    ]

    monkeypatch.setattr(database, "DB_PATH", db_path)
    monkeypatch.setattr(setup_database, "DB_PATH", db_path)
    monkeypatch.setattr(
        setup_database,
        "load_financial_data",
        lambda: records,
    )

    setup_database.setup_database()

    return db_path


def test_read_financial_data(temporary_database):
    result = database.get_financial_data("DemoCo", 2024)

    assert result["revenue"] == 1_350_000
    assert result["operating_profit"] == 162_000
    assert result["currency"] == "PLN"
    assert result["unit"] == 1
    assert result["source"] == "synthetic_demo"


def test_company_name_matching(temporary_database):
    result = database.get_financial_data("  democo  ", 2024)

    assert result["company"] == "DemoCo"


def test_missing_year(temporary_database):
    with pytest.raises(ValueError, match="Brak danych"):
        database.get_financial_data("DemoCo", 2025)


def test_missing_database(temporary_database):
    temporary_database.unlink()

    with pytest.raises(FileNotFoundError):
        database.get_financial_data("DemoCo", 2024)

    # Odczyt nie powinien tworzyć nowej, pustej bazy.
    assert not temporary_database.exists()


def test_repeated_import_does_not_duplicate(temporary_database):
    setup_database.setup_database()

    connection = sqlite3.connect(temporary_database)

    try:
        count = connection.execute(
            "SELECT COUNT(*) FROM financials"
        ).fetchone()[0]
    finally:
        connection.close()

    assert count == 1


def test_company_input_is_not_sql(temporary_database):
    with pytest.raises(ValueError, match="Brak danych"):
        database.get_financial_data(
            "DemoCo' OR 1=1 --",
            2024,
        )