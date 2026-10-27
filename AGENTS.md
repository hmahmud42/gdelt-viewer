# AGENTS.md

> THIS IS AI GENERATED - NEEDS TO BE UPDATED

## Project Identity & Tech Stack
- Framework: Streamlit (Python 3.11+)
- HTTP Client: `httpx` or `requests` for fetching external data
- Data Processing: `pandas`
- Caching Strategy: Streamlit native caching (`@st.cache_data`, `@st.cache_resource`)

## Essential Commands
- Run app locally: `streamlit run app.py`
- Install dependencies: `pip install -r requirements.txt`
- Run linter/formatter: `ruff check . && ruff format .`
- Run tests: `pytest`

## Operational Rules & Boundaries

### 🟢 ALWAYS DO
- Use `@st.cache_data` with an explicit `ttl` (Time-To-Live) for all external HTTP fetch operations to prevent API throttling.
- Implement robust exception handling (`try-except` blocks) for all HTTP network calls to gracefully catch timeouts, 4xx, and 5xx errors.
- Display clean, user-friendly error messages using `st.error()` or `st.warning()` if the external data store is unreachable.
- Use `st.dataframe()` or `st.data_editor()` for rendering data tabularly, ensuring memory limits aren't exceeded by slicing massive datasets.

### 🟡 ASK FIRST
- Before introducing new third-party plotting or visualization libraries (prefer native Streamlit elements or Plotly/Altair if already installed).
- Before refactoring the core state-management pattern (`st.session_state`).

### 🔴 NEVER DO
- Never make un-cached HTTP requests inside loops or on every Streamlit script rerun.
- Never hardcode URLs, API keys, or endpoint credentials (always use `st.secrets` or `.env` variables via `os.environ`).
- Never perform heavy data processing or long-running computations on the main Streamlit thread without a loader component (`st.spinner`).

## Project Topology & Pointers
- App Feature Roadmap & NLP Workflow: Read @docs/workflow.md


## Operational Rules & Boundaries

### 🟢 ALWAYS DO
- Mock all HTTP networking calls inside tests using `pytest-mock` or `responses`.
- Use a local mock dataset (e.g., dummy JSON/CSV files in @tests/mock_data/) for verifying UI rendering.

### 🔴 NEVER DO
- **NEVER trigger live HTTP requests to the public data source during code generation, linting, or automated test suites.** 
- Live integration testing and production execution are strictly restricted to the human developer.
- Never write code that lacks local mock fallbacks for network actions.


