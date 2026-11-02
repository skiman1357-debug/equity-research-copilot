import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, APIStatusError

from agent import run_agent


st.set_page_config(
    page_title="Equity Research Copilot",
    page_icon="📊",
    layout="wide",
)

project_dir = Path(__file__).resolve().parent
load_dotenv(project_dir / ".env", override=True)

api_key = os.getenv("XAI_API_KEY", "").strip()
model = os.getenv("XAI_MODEL", "").strip()


st.title("Equity Research Copilot")
st.write(
    "Analizuj wyniki finansowe i sprawdzaj wyjaśnienia "
    "w raportach źródłowych."
)

with st.sidebar:
    st.header("Dostępne dane")
    st.markdown(
        """
        **cyber_Folks — grupa kapitałowa**
        - Dane finansowe: 2024–2025
        - Dane za 2024 rok: przekształcone
        - Sprawozdanie finansowe za 2025
        - Sprawozdanie zarządu za 2025

        **DemoCo**
        - Fikcyjne dane: 2022–2024
        - Bez raportów źródłowych
        """
    )

    st.caption(
        "Wyszukiwanie w raportach korzysta ze słów kluczowych. "
        "Każde pytanie rozpoczyna osobną analizę."
    )


if not api_key or not model:
    st.error("Uzupełnij XAI_API_KEY i XAI_MODEL w pliku .env.")
    st.stop()

if not (project_dir / "data" / "financials.db").is_file():
    st.error("Brakuje bazy danych. Uruchom setup_database.py.")
    st.stop()


default_question = (
    "Czy wzrost przychodów grupy cyber_Folks w 2025 roku "
    "wynikał wyłącznie ze wzrostu organicznego? "
    "Oblicz dynamikę względem 2024 roku i podaj "
    "wyjaśnienia zarządu wraz ze źródłami i stronami."
)

with st.form("analysis_form"):
    question = st.text_area(
        "Twoje pytanie",
        value=default_question,
        height=150,
        max_chars=3000,
    )

    submitted = st.form_submit_button("Przeanalizuj")

st.caption(
    "Analiza korzysta z płatnego API xAI. "
    "Jedno pytanie może wymagać kilku zapytań do modelu."
)


if submitted:
    if not question.strip():
        st.warning("Najpierw wpisz pytanie.")
    else:
        events = []

        analysis = {
            "question": question.strip(),
            "answer": "",
            "events": events,
            "error": "",
        }

        with st.spinner("Agent sprawdza dane i przygotowuje odpowiedź..."):
            try:
                with OpenAI(
                    api_key=api_key,
                    base_url="https://api.x.ai/v1",
                    timeout=60.0,
                    max_retries=0,
                ) as client:
                    analysis["answer"] = run_agent(
                        client=client,
                        model=model,
                        question=question.strip(),
                        on_event=events.append,
                    )

            except APIConnectionError:
                analysis["error"] = (
                    "Nie udało się połączyć z API. "
                    "Sprawdź internet i spróbuj ponownie."
                )

            except APIStatusError as error:
                details = error.response.text.replace(
                    api_key,
                    "[UKRYTY KLUCZ]",
                )
                analysis["error"] = (
                    f"Błąd API HTTP {error.status_code}: {details}"
                )

        st.session_state["last_analysis"] = analysis


if "last_analysis" in st.session_state:
    analysis = st.session_state["last_analysis"]

    st.divider()
    st.subheader("Ostatnia analiza")
    st.write(analysis["question"])

    if analysis["error"]:
        st.error(analysis["error"])
    else:
        st.markdown(analysis["answer"])

    st.subheader("Podgląd wykonanych narzędzi")

    if not analysis["events"]:
        st.info("Nie zarejestrowano wywołań narzędzi.")

    for number, event in enumerate(analysis["events"], start=1):
        status = "OK" if event["result"]["ok"] else "BŁĄD"

        with st.expander(
            f"{number}. {event['tool']} — {status}"
        ):
            st.markdown("**Argumenty**")

            try:
                st.json(json.loads(event["arguments"]))
            except json.JSONDecodeError:
                st.code(event["arguments"])

            st.markdown("**Wynik narzędzia**")
            st.json(event["result"])