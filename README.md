# Equity Research Copilot

A personal portfolio project that combines financial analysis with an LLM agent. The application retrieves financial data from SQLite, calculates operating margins and revenue growth using Python functions, and searches company reports to support explanations with document names and page references.

Built by Hubert Kaczmarski as a transition project from equity research into software and AI engineering.

## What it does

- Answers questions through a local Streamlit interface or a command-line interface.
- Uses Grok through the xAI Responses API to select and call Python tools.
- Retrieves company and year-specific financial records from a read-only SQLite connection.
- Calculates operating margin and revenue growth in Python.
- Searches two cyber_Folks reports using keyword matching.
- Displays tool arguments and results in expandable sections in the interface.
- Reports missing data instead of substituting records from another period.

## Example

**Question:** Was cyber_Folks Group's revenue growth in 2025 entirely organic? Calculate growth versus 2024 and cite management's explanations.

The agent can retrieve 2024 and 2025 revenue, call the revenue-growth calculator, search the reports, and produce an answer with citations.

Verified numerical result: **30.29% reported revenue growth**. Retrieved management commentary discusses both organic development and consolidation of acquired companies. The example does not establish an exact quantitative split between those effects.

## Architecture

1. Streamlit collects a question; each submission starts a separate analysis.
2. The application sends tool definitions and instructions to Grok.
3. Grok requests tools and supplies their arguments.
4. Python validates the arguments and executes only functions in an explicit allowlist.
5. Tool results are returned to the model using the response continuation ID.
6. The loop continues until a text answer is returned or a configured limit is reached.

Current limits: at most 6 model requests and 12 tool calls per analysis. These are execution limits, not a monetary budget.

### Tools

| Tool | Responsibility |
| --- | --- |
| `get_financial_data(company, year)` | Parameterized SQL query for one financial record. |
| `calculate_operating_margin(revenue, operating_profit)` | Operating profit divided by revenue, expressed as a percentage. |
| `calculate_revenue_growth(previous_revenue, current_revenue)` | Percentage change in revenue between two periods. |
| `search_report(query, top_k)` | Returns up to 5 report fragments with document names and page numbers. |

Report retrieval is a simple lexical approach: documents are split into approximately 1,800-character fragments with 300-character overlap. Fragments are ranked by the proportion of query terms present. It does not use embeddings, a vector database, semantic search, or a trained financial model. Retrieval scores are not confidence scores.

## Technology

Python, SQLite (`sqlite3`), Streamlit, pytest, python-dotenv, and the OpenAI Python SDK configured with the xAI endpoint. Python's standard XML parser reads the XHTML reports. No OpenAI API key is required; the application uses an **xAI API key**.

## Data and sources

| Dataset | Period | Scope and units |
| --- | --- | --- |
| cyber_Folks | 2024–2025 | Consolidated group figures; PLN thousands (`unit=1000`). 2024 figures are restated comparatives from the 2025 report. |
| DemoCo | 2022–2024 | Synthetic demonstration figures; PLN (`unit=1`). No supporting reports. |

The financial CSV contains manually selected and verified figures, not automatically extracted financial tables.

| cyber_Folks metric (PLN thousands) | 2024 restated | 2025 |
| --- | ---: | ---: |
| Revenue | 656,331 | 855,151 |
| Operating profit | 133,618 | 207,078 |
| Operating margin | 20.36% | 24.22% |

Primary sources:

- [2025 consolidated financial statements](https://investors.cyberfolks.pl/wp-content/uploads/2026/05/CBF-2025-12-31-1-pl.xhtml): income statement on page 5; comparative restatement on page 17.
- [2025 management report](https://investors.cyberfolks.pl/wp-content/uploads/2026/05/CBF2025_raport_roczny_work_xsm.xhtml): management commentary on pages 39 and 73.

Source documents remain the property of their respective owners. Download them from the original publisher using the instructions below. The agent searches local copies and does not browse the web at runtime.

## Setup — Windows / PowerShell

Prerequisites: Python 3.12 or 3.13, Git, and an xAI API account with access to the configured model and sufficient API credits.

Clone this repository or download its ZIP, then open a terminal in the project directory.

### 1. Create an environment and install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Using the environment's interpreter directly avoids requiring PowerShell activation.

### 2. Configure the API

```powershell
Copy-Item .env.example .env
```

Edit `.env` locally:

```dotenv
XAI_API_KEY=your_xai_api_key
XAI_MODEL=grok-4.7
```

The model identifier above was used during development. If it is unavailable for your account, select an available xAI model supporting the Responses API and function calling. Never commit the real `.env` file.

### 3. Download the two source reports

Run these commands in PowerShell from the project directory:

```powershell
New-Item -ItemType Directory -Force reports | Out-Null
Invoke-WebRequest -Uri "https://investors.cyberfolks.pl/wp-content/uploads/2026/05/CBF-2025-12-31-1-pl.xhtml" -OutFile "reports/CBF-2025-12-31-1-pl.xhtml"
Invoke-WebRequest -Uri "https://investors.cyberfolks.pl/wp-content/uploads/2026/05/CBF2025_raport_roczny_work_xsm.xhtml" -OutFile "reports/CBF2025_raport_roczny_work_xsm.xhtml"
```

Preserve these filenames. If the publisher changes its URLs or document structure, downloading or parsing may need to be updated.

### 4. Create the database

```powershell
.\.venv\Scripts\python.exe setup_database.py
```

With the current CSV, the database contains five records. Re-running the importer updates existing company/year records without duplicating them. Removing a row from the CSV does not delete that row from an existing database.

### 5. Run tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

The current suite contains **24 tests** covering financial calculations, CSV loading, and SQLite access/import behavior. These tests do not call the paid API and do not require the downloaded reports. They do not constitute automated coverage of the agent loop, report retrieval, or Streamlit interface.

### 6. Run the application

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address localhost
```

Open the local URL printed in the terminal, normally `http://localhost:8501`. Keep the terminal running; stop with Ctrl+C. Each submitted analysis can make multiple paid API requests.

Optional command-line mode:

```powershell
.\.venv\Scripts\python.exe agent.py
```

## Project files

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit interface and tool execution display. |
| `agent.py` | Model instructions, tool definitions, validation, and execution loop. |
| `financial_tools.py` | Financial calculations. |
| `data_loader.py` | CSV parsing and record validation. |
| `setup_database.py` | Creates SQLite tables and imports CSV records. |
| `database.py` | Read-only, parameterized financial-data retrieval. |
| `report_reader.py` | Page-aware parsing of the two report formats. |
| `report_search.py` | Cached keyword index and fragment retrieval. |
| `data/financials.csv` | Reproducible source for the local database. |
| `tests/` | Automated unit and data-layer tests. |
| `check_*.py` | Manual checks for calculations, data, reports, and search. |
| `main.py` | Initial API connection smoke test; invokes the paid API. |

## Manual evaluation

Observed successful scenarios during development:

| Scenario | Expected / observed behavior |
| --- | --- |
| DemoCo 2024 margin and growth vs 2023 | 12.00% margin and 12.50% revenue growth. |
| DemoCo 2025 margin | Reports missing data without inventing a result. |
| Whether wages caused DemoCo's margin decline | Calculates margins but does not claim an unsupported cause. |
| cyber_Folks 2025 revenue growth | 30.29%, with correct units and restated comparative disclosure. |
| Organic growth versus acquisitions | Combines SQL data, calculation, and retrieved management commentary with page references. |
| Unknown search keyword | Returns no matching fragments. |

These are example runs, not a statistically representative accuracy benchmark. LLM outputs can vary.

## Limitations

- A learning prototype focused on one real company and one synthetic dataset.
- No live prices, forecasts, DCF valuation, or trading functionality.
- Keyword search does not understand synonyms or Polish inflections and can return irrelevant fragments.
- The XHTML reader is tailored to the two supplied report structures; it is not a general document parser.
- Extracted tables can lose their visual layout. Calculations therefore use curated SQLite records.
- Citations and factual explanations are generated by the model and still require review.
- Some rules, such as period and unit consistency in model-selected calculations, rely on instructions rather than fully enforced end-to-end provenance checks.
- Prompt-injection resistance has not been comprehensively evaluated.
- No authentication or production deployment configuration. The supplied launch command binds to localhost.
- Submitted questions, selected financial records, and retrieved report fragments are sent to xAI during analysis.

## Development approach and AI assistance

Developed with AI assistance for implementation, explanations, debugging, and test design. My contribution included defining the financial use case, selecting source reports, checking financial figures and units, running the application and tests locally, and reviewing tool traces and responses. This project documents practical learning and does not imply independent mastery of every technology used.

## Suggested 60–90 second demo

1. Introduce the problem: checking financial performance and finding supporting explanations across reports.
2. Submit the cyber_Folks organic-growth question shown above.
3. Show the 30.29% result, correct units, and source references.
4. Expand the data retrieval, calculation, and report-search tool events.
5. Submit: `Podaj marżę operacyjną DemoCo za 2025 rok.` Show the missing-data response.
6. Close with the architecture and one limitation: keyword retrieval can miss relevant wording, so answers require verification.

API latency may make the live demonstration longer. For a recording, shorten waiting periods and disclose that they were edited.
