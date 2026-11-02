import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, APIStatusError


# Odczytujemy plik .env znajdujący się obok main.py.
env_path = Path(__file__).resolve().parent / ".env"

if not env_path.is_file():
    raise SystemExit("Brakuje pliku .env obok main.py.")

load_dotenv(env_path, override=True)

api_key = os.getenv("XAI_API_KEY", "").strip()
model = os.getenv("XAI_MODEL", "").strip()

if not api_key:
    raise SystemExit("Uzupełnij XAI_API_KEY w pliku .env.")

if not model:
    raise SystemExit("Uzupełnij XAI_MODEL w pliku .env.")

# Konfigurujemy połączenie z xAI.
client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1",
    timeout=60.0,
    max_retries=0,
)

print("Klucz wczytany. Łączę się z Grokiem...")

try:
    response = client.responses.create(
        model=model,
        input=(
            "Odpowiedz po polsku jednym krótkim zdaniem: "
            "do czego służy marża operacyjna?"
        ),
    )

    print("\nOdpowiedź Groka:")
    print(response.output_text)

except APIConnectionError:
    print("Nie udało się połączyć z API. Sprawdź internet i spróbuj ponownie.")

except APIStatusError as error:
    print(f"API zwróciło błąd HTTP {error.status_code}.")
    print("Wybrany model:", model)

    # Pokazujemy odpowiedź serwera, usuwając klucz, gdyby się pojawił.
    details = error.response.text.replace(api_key, "[UKRYTY KLUCZ]")
    print("Szczegóły błędu:", details)