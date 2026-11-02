from report_search import search_report


result = search_report(
    query="Shoper Hosterion konsolidacja",
    top_k=3,
)

print("Zapytanie:", result["query"])
print("Znaleziono fragmenty:", result["found"])

for number, fragment in enumerate(result["results"], start=1):
    print(f"\n=== WYNIK {number} ===")
    print("Dokument:", fragment["source"])
    print("Strona:", fragment["page"])
    print("Fragment:", fragment["chunk"])
    print("Dopasowane słowa:", ", ".join(fragment["matched_terms"]))
    print("Wynik dopasowania:", round(fragment["score"], 2))
    print("\nTreść:")
    print(fragment["text"])

print("\n=== SPRAWDZENIE BRAKU TRAFIEŃ ===")

missing = search_report("zzzznieistniejacehaslo987654")

print("Znaleziono fragmenty:", missing["found"])
print("Liczba wyników:", len(missing["results"]))