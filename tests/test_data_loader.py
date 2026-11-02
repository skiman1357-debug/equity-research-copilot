import pytest

import data_loader


@pytest.fixture
def sample_csv(tmp_path, monkeypatch):
    """Tworzy osobny, tymczasowy plik tylko dla testów."""
    path = tmp_path / "financials.csv"

    path.write_text(
        "company,year,revenue,operating_profit,currency,unit,source\n"
        "DemoCo,2023,1200000,180000,PLN,1,synthetic_demo\n"
        "DemoCo,2024,1350000,162000,PLN,1,synthetic_demo\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(data_loader, "DATA_PATH", path)

    return path


def test_get_existing_data(sample_csv):
    result = data_loader.get_financial_data("DemoCo", 2024)

    assert result["revenue"] == 1_350_000
    assert result["operating_profit"] == 162_000
    assert result["currency"] == "PLN"
    assert result["unit"] == 1
    assert result["source"] == "synthetic_demo"


def test_company_name_ignores_case_and_spaces(sample_csv):
    result = data_loader.get_financial_data("  democo  ", 2024)

    assert result["company"] == "DemoCo"


def test_missing_year(sample_csv):
    with pytest.raises(ValueError, match="Brak danych"):
        data_loader.get_financial_data("DemoCo", 2025)


def test_duplicate_records(sample_csv):
    with sample_csv.open("a", encoding="utf-8") as file:
        file.write(
            "DemoCo,2024,1350000,162000,PLN,1,synthetic_demo\n"
        )

    with pytest.raises(ValueError, match="Powtórzone dane"):
        data_loader.load_financial_data()


def test_missing_columns(sample_csv):
    sample_csv.write_text(
        "company,year\nDemoCo,2024\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="kolumn"):
        data_loader.load_financial_data()


def test_missing_file(sample_csv):
    sample_csv.unlink()

    with pytest.raises(FileNotFoundError):
        data_loader.load_financial_data()