import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, APIStatusError

from agent import run_agent
from deployment import access_allowed, prepare_data


st.set_page_config(
    page_title="Equity Research Copilot",
    page_icon="📊",
    layout="wide",
)

project_dir = Path(__file__).resolve().parent
load_dotenv(project_dir / ".env", override=False)

def setting(name):
    try:
        value = st.secrets.get(name)
    except FileNotFoundError:
        value = None
    return str(value if value is not None else os.getenv(name, "")).strip()


@st.cache_resource(show_spinner=False)
def initialize_data():
    prepare_data()
    return True


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


mode = st.radio("Tryb", ["Przykład bez API", "Analiza na żywo"], horizontal=True)

if mode == "Przykład bez API":
    st.info("Zapisane podsumowanie wcześniejszego testu. Ten widok nie wywołuje AI.")
    st.subheader("Czy wzrost przychodów cyber_Folks w 2025 był wyłącznie organiczny?")
    st.markdown("""
**Przychody:** 656 331 tys. PLN w 2024 → 855 151 tys. PLN w 2025.
**Dynamika raportowanych przychodów: +30,29%.**

Komentarz zarządu wskazuje zarówno wzrost organiczny, jak i konsolidację
Shoper od lutego oraz Hosterion od czerwca 2025 r. Przytoczone fragmenty
nie pozwalają wyliczyć udziału każdego czynnika w całkowitej dynamice.
Dane 2024 są przekształcone; porównanie dotyczy grupy kapitałowej.

Źródła: [sprawozdanie finansowe, s. 5](https://investors.cyberfolks.pl/wp-content/uploads/2026/05/CBF-2025-12-31-1-pl.xhtml)
i [raport zarządu, s. 39 i 73](https://investors.cyberfolks.pl/wp-content/uploads/2026/05/CBF2025_raport_roczny_work_xsm.xhtml).

[Obejrzyj nagranie dema](https://www.youtube.com/watch?v=tvC2XNsOvrg)
· [Kod projektu](https://github.com/skiman1357-debug/equity-research-copilot)
""")
    st.stop()

api_key = setting("XAI_API_KEY")
model = setting("XAI_MODEL")
access_code = setting("DEMO_ACCESS_CODE")

if not api_key or not model or not access_code:
    st.info("Analiza na żywo jest obecnie niedostępna. Możesz obejrzeć przykład bez API.")
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

    provided_code = st.text_input("Kod dostępu do analizy na żywo", type="password")
    submitted = st.form_submit_button("Przeanalizuj")

st.caption(
    "Analiza korzysta z płatnego API xAI. "
    "Pytanie i wykorzystane fragmenty raportów są przesyłane do xAI."
)


if submitted:
    if not access_allowed(provided_code, access_code):
        st.error("Nieprawidłowy kod dostępu.")
        st.stop()
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
                initialize_data()
            except Exception:
                st.error("Nie udało się przygotować danych lub pobrać raportów. Spróbuj ponownie później.")
                st.stop()
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
                analysis["error"] = (
                    f"Usługa AI zwróciła błąd HTTP {error.status_code}. "
                    "Spróbuj ponownie później lub skontaktuj się z autorem aplikacji."
                )
            except Exception:
                analysis["error"] = "Analiza nie powiodła się. Spróbuj ponownie później."


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