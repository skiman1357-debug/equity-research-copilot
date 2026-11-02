from pathlib import Path
import xml.etree.ElementTree as ET


REPORTS_DIR = Path(__file__).resolve().parent / "reports"

REPORT_FILES = [
    "CBF-2025-12-31-1-pl.xhtml",
    "CBF2025_raport_roczny_work_xsm.xhtml",
]


def tag_name(element):
    """Usuwa przestrzeń nazw XML z nazwy elementu."""
    return element.tag.rsplit("}", 1)[-1]


def extract_text(element):
    """Łączy fragmenty tekstu, zachowując granice akapitów."""
    tag = tag_name(element)

    if tag in {"script", "style", "head"}:
        return ""

    parts = [element.text or ""]

    for child in element:
        parts.append(extract_text(child))
        parts.append(child.tail or "")

    text = "".join(parts)

    if tag in {"div", "p", "tr", "h1", "h2", "h3", "li", "br"}:
        return "\n" + text + "\n"

    if tag in {"td", "th"}:
        return " " + text + " "

    return text


def read_report(filename):
    """Zwraca listę stron zawierających tekst i nazwę źródła."""
    if filename not in REPORT_FILES:
        raise ValueError("Nieznany raport.")

    path = REPORTS_DIR / filename

    if not path.is_file():
        raise FileNotFoundError(
            f"Nie znaleziono raportu: {path}"
        )

    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as error:
        raise ValueError(
            f"Nie można odczytać XHTML: {filename}. "
            "Sprawdź, czy zapisano oryginalny dokument."
        ) from error

    # Format sprawozdania finansowego.
    pages = [
        element
        for element in root.iter()
        if tag_name(element) == "div"
        and "page-container" in element.get("class", "").split()
    ]

    # Format sprawozdania zarządu.
    if not pages:
        pages = [
            element
            for element in root.iter()
            if tag_name(element) == "div"
            and "pf" in element.get("class", "").split()
        ]

    if not pages:
        raise ValueError(
            f"Nie rozpoznano podziału na strony: {filename}"
        )

    results = []

    for page_number, element in enumerate(pages, start=1):
        raw_text = extract_text(element)

        # Usuwamy nadmiarowe spacje i puste linie.
        lines = [
            " ".join(line.split())
            for line in raw_text.splitlines()
            if line.strip()
        ]

        results.append({
            "source": filename,
            "page": page_number,
            "text": "\n".join(lines),
        })

    return results