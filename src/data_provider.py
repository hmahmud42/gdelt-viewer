"""
GEMINI GENERATED - REVIEW NEEDED
"""

import os
import json
import time
import httpx
import pandas as pd
import streamlit as st
from datetime import datetime, timezone
from typing import Optional

from consts import LAST_RETRIEVED_PATH, UPDATE_CHECK_INTERVAL_SECONDS

# Strict environment gate
IS_MOCK = os.getenv("APP_ENV", "development") == "development"
MOCK_DATA_PATH = "tests/mock_data/sample_files.json"

@st.cache_data(ttl=3600)
def fetch_file_list() -> list[dict]:
    """
    Fetches the latest list of files from the public endpoint.
    Enforces local mock fallbacks during development/agent cycles.
    """
    if IS_MOCK:
        # Load local mock file safely
        if not os.path.exists(MOCK_DATA_PATH):
            raise FileNotFoundError(f"Mock data registry missing at: {MOCK_DATA_PATH}")
        with open(MOCK_DATA_PATH, "r") as f:
            return json.load(f)
            
    # Production Live Logic (Human-Triggered Only)
    url = "https://public-project-host.org"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        st.error(f"Network error accessing external store: {e}")
        return []

def _read_last_retrieved() -> Optional[float]:
    """Read the unix timestamp of the last successful retrieval from local state.

    Returns None when the state file is missing or unreadable (first run).
    """
    try:
        with open(LAST_RETRIEVED_PATH, "r") as f:
            state = json.load(f)
        last_retrieved = state.get("last_retrieved") if isinstance(state, dict) else state
        return float(last_retrieved) if last_retrieved is not None else None
    except (OSError, ValueError, TypeError):
        # Missing or corrupt state file -> treat as a first run.
        return None

def _write_last_retrieved(timestamp: float) -> None:
    """Persist the unix timestamp of the last retrieval to local state."""
    os.makedirs(os.path.dirname(LAST_RETRIEVED_PATH) or ".", exist_ok=True)
    with open(LAST_RETRIEVED_PATH, "w") as f:
        json.dump({"last_retrieved": timestamp}, f)

def _file_entry_timestamp(entry: dict) -> Optional[float]:
    """Extract the publish time (unix seconds) from a GDELT file entry.

    GDELT file names are prefixed with a 14-digit UTC timestamp, eg.
    "20261025000000.export.CSV".
    """
    filename = str(entry.get("filename") or entry.get("name") or "")
    if len(filename) < 14 or not filename[:14].isdigit():
        return None
    return datetime.strptime(
        filename[:14], "%Y%m%d%H%M%S"
    ).replace(tzinfo=timezone.utc).timestamp()

def get_update_filename() -> list[str]:
    """
    Generates a list of file names to retrieve from GDELT that were added since the
    last time the data was checked.

    GDELT updates its file listing every 15 minutes, and makes the names of the latest
    files available at a single location (see `fetch_file_list`).

    The time-stamp of the last data retrieval is stored locally in
    @data/last_retrieved.json (which may be absent).

    - If the time-stamp is absent, or less than 20 minutes old, return an empty list.
    - Otherwise, infer the names of all the files that have been added since the last
      update and return that list.

    Returns
    -------
    list[str]
        File names (eg. "20261025000000.export.CSV") that are new since the last check.
        Empty if no new files have been published (or if the check is still cooling down).
    """
    latest_files = fetch_file_list()
    if not latest_files:
        return []

    last_retrieved = _read_last_retrieved()
    now = time.time()

    if last_retrieved is not None and (now - last_retrieved) < UPDATE_CHECK_INTERVAL_SECONDS:
        # We checked very recently, so the listing is unlikely to have changed.
        return []

    cutoff = last_retrieved if last_retrieved is not None else 0.0
    new_filenames = []
    for entry in latest_files:
        entry_timestamp = _file_entry_timestamp(entry)
        if entry_timestamp is None or entry_timestamp <= cutoff:
            continue
        new_filenames.append(str(entry.get("filename") or entry.get("name") or ""))

    _write_last_retrieved(now)
    return new_filenames

def process_nlp_keywords(file_data: list[dict], keywords: list[str]) -> pd.DataFrame:
    """
    Local non-LLM/NLP filtering logic over downloaded data arrays.
    """
    matched_records = []
    keywords_lower = [k.lower() for k in keywords]
    
    for item in file_data:
        title = item.get("title", "").lower()
        description = item.get("description", "").lower()
        
        # Simple local keyword check
        if any(kw in title or kw in description for kw in keywords_lower):
            matched_records.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "topic": item.get("category", "General"),
                "tagged_for_analysis": False,
                "analysis_type": "None"
            })
            
    return pd.DataFrame(matched_records)
