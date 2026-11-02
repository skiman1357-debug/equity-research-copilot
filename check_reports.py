from report_reader import REPORT_FILES, read_report


for filename in REPORT_FILES:
    pages = read_report(filename)

    empty_pages = sum(
        not page["text"].strip()
        for page in pages
    )

    print(f"\nRaport: {filename}")
    print(f"Liczba stron: {len(pages)}")
    print(f"Puste strony: {empty_pages}")

    if filename == "CBF-2025-12-31-1-pl.xhtml":
        page_number = 5
    else:
        page_number = 73

    selected_page = pages[page_number - 1]

    print(f"\n--- Fragment strony {page_number} ---")
    print(selected_page["text"][:1800])