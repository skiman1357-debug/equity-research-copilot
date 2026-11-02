import re
from functools import lru_cache

from report_reader import REPORT_FILES, read_report


def tokenize(text):
    """Zamienia tekst na zbiór słów zapisanych małymi literami."""
    return set(re.findall(r"\w+", text.casefold()))


@lru_cache(maxsize=1)
def build_search_index():
    """Wczytuje raporty i dzieli strony na krótsze fragmenty."""
    index = []

    chunk_size = 1800
    overlap = 300

    for filename in REPORT_FILES:
        pages = read_report(filename)

        for page in pages:
            text = page["text"]
            start = 0
            chunk_number = 1

            while start < len(text):
                end = min(start + chunk_size, len(text))

                # Jeśli to możliwe, kończymy fragment na granicy słowa.
                if end < len(text):
                    boundary = text.rfind(" ", start, end)
                    if boundary > start + chunk_size // 2:
                        end = boundary

                fragment = text[start:end].strip()

                if fragment:
                    index.append({
                        "source": page["source"],
                        "page": page["page"],
                        "chunk": chunk_number,
                        "text": fragment,
                        "tokens": tokenize(fragment),
                    })

                if end == len(text):
                    break

                start = max(start + 1, end - overlap)
                chunk_number += 1

    return index


def search_report(query, top_k=3):
    """Zwraca fragmenty raportów pasujące do słów kluczowych."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Podaj niepuste zapytanie.")

    if type(top_k) is not int or not 1 <= top_k <= 5:
        raise ValueError("top_k musi być liczbą całkowitą od 1 do 5.")

    query_tokens = tokenize(query)

    if not query_tokens:
        raise ValueError("Zapytanie musi zawierać słowa lub liczby.")

    candidates = []

    for fragment in build_search_index():
        matched = query_tokens & fragment["tokens"]

        if not matched:
            continue

        candidates.append({
            "source": fragment["source"],
            "page": fragment["page"],
            "chunk": fragment["chunk"],
            "matched_terms": sorted(matched),
            "score": len(matched) / len(query_tokens),
            "text": fragment["text"],
        })

    # Najpierw fragmenty zawierające najwięcej słów z zapytania.
    candidates.sort(
        key=lambda item: (
            -item["score"],
            item["source"],
            item["page"],
            item["chunk"],
        )
    )

    results = candidates[:top_k]

    return {
        "query": query,
        "found": bool(results),
        "results": results,
        "note": (
            "Wyniki dopasowano po słowach kluczowych. "
            "Brak trafień nie dowodzi braku informacji w raportach."
        ),
    }