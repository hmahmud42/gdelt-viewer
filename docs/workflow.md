# App Workflow Specification

> THIS IS AI GENERATED - NEEDS TO BE UPDATED

## Phase 1: Data Acquisition (Human-Triggered Only)
1. Fetch listing of latest available data files from the HTTP destination.
2. Download target payload files locally to a cache directory (`.data_cache/`).

## Phase 2: Analysis Engine
1. Parse local payload files.
2. Apply local keyword and basic NLP filtering rules to identify topic relevance (Note: Do not use LLM/API-based tokens here; rely on local processing).
3. Extract relevant hyperlinks mapped to identified topics.

## Phase 3: Streamlit Interface & Curation Workflow
1. Render a clean list of extracted hyperlinks matching the chosen topic.
2. Provide interactive mechanisms (e.g., checkbox, button, or `st.data_editor`) allowing the user to click the link and "tag" it.
3. Save tagged records and their specified analysis profiles to a local configuration state for future processing phases.
