# Publikacja Equity Research Copilot

To aktualizacja istniejącego projektu, nie cały projekt. Skopiuj zawartość
paczki do folderu z obecnym app.py. Zachowaj pozostałe pliki i testy.
Jeśli masz własne dodatkowe reguły .gitignore, zachowaj je.

## Lokalnie

W terminalu PyCharma, z aktywnym .venv:

```powershell
python -m pip install -r requirements.txt
python -m pytest tests -q
python -m streamlit run app.py
```

Przykład bez API działa bez konfiguracji. Analiza na żywo wymaga ustawień
XAI_API_KEY, XAI_MODEL oraz DEMO_ACCESS_CODE w lokalnym .env albo Secrets.
Zachowaj swój działający klucz i dokładny identyfikator modelu. Dodaj własny,
długi losowy kod dostępu. Sekrety Streamlit mają pierwszeństwo przed .env.

## GitHub

Wykonuj komendy kolejno. Jeśli gałąź już istnieje, zamiast tworzyć ją ponownie
przełącz się na nią przez git switch deploy/streamlit-cloud.

```powershell
git switch -c deploy/streamlit-cloud
git add app.py deployment.py requirements.txt .gitignore tests/test_deployment.py DEPLOY_STREAMLIT.md
git commit -m "Prepare Streamlit Cloud demo with protected live analysis"
git push -u origin deploy/streamlit-cloud
```

## Streamlit Community Cloud

Otwórz https://share.streamlit.io/ i połącz swoje konto GitHub. Wybierz Create app.

- Repository: skiman1357-debug/equity-research-copilot
- Branch: deploy/streamlit-cloud
- Main file path: app.py
- Advanced settings / Python: 3.12

W Advanced settings / Secrets wklej własne wartości zamiast placeholderów:

```toml
XAI_API_KEY = "TWOJ_KLUCZ_XAI"
XAI_MODEL = "DOKLADNY_MODEL_Z_DZIALAJACEGO_ENV"
DEMO_ACCESS_CODE = "TWOJ_DLUGI_LOSOWY_KOD"
```

Kliknij Save i Deploy. Nie wysyłaj tych wartości do GitHuba ani w rozmowie.
Bez Secrets działa tylko publiczny przykład. Kod dostępu przekaż rekruterowi
osobno; nie umieszczaj go w README. To prosta ochrona dema, nie limit wydatków
ani pełny system kont. Osoby znające kod mogą wykonywać wiele płatnych analiz.
Usunięcie kodu z Secrets wyłącza tryb live.

Przy pierwszej autoryzowanej analizie aplikacja przygotuje bazę z CSV i pobierze
brakujące raporty z oficjalnych adresów. Może to potrwać dłużej. Po restarcie
serwera dane mogą być przygotowywane ponownie. Awaria źródła raportów nie
blokuje wyświetlania publicznego przykładu.

## Kontrola po wdrożeniu

1. Sprawdź publiczny przykład w prywatnym oknie przeglądarki.
2. Błędny kod powinien blokować analizę.
3. Z poprawnym kodem zapytaj o DemoCo 2024: marża 12%, dynamika 12,5%.
4. Zapytaj o DemoCo 2025: oczekuj informacji o braku danych.
5. Zapytaj o cyber_Folks 2025: dynamika 30,29% i źródła ze stronami.

Paczka dodaje 12 przypadków testowych do wcześniejszych 24. Testy nie wykonują
płatnych zapytań. Działanie z prawdziwym kluczem trzeba sprawdzić po wdrożeniu.

Dokumentacja:
https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
