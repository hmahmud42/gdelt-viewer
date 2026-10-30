"""Load news coverage data from the GDELT Project DOC API."""

import time
from typing import Optional

import pandas as pd

from gdeltdoc import GdeltDoc, Filters

DEFAULT_KEYWORD = "climate change"
DEFAULT_TIMESPAN = "30d"

# The GDELT DOC API only allows one request every 5 seconds.
_MIN_REQUEST_INTERVAL_SECONDS = 6


_last_api_call: float = 0.0


def _wait_for_rate_limit() -> None:
    """Sleep so we do not exceed GDELT's one-request-per-5-seconds limit."""
    global _last_api_call

    now = time.monotonic()
    wait = _last_api_call + _MIN_REQUEST_INTERVAL_SECONDS - now
    if wait > 0:
        time.sleep(wait)
    _last_api_call = time.monotonic()


def get_gdelt_client():
    """Create a client for the GDELT DOC API."""
    return GdeltDoc()


def load_climate_articles(
    keyword: str = DEFAULT_KEYWORD,
    timespan: str = DEFAULT_TIMESPAN,
    max_records: int = 25,
) -> pd.DataFrame:
    """Fetch recent news articles matching the given keyword.

    Uses the GDELT DOC API "ArtList" mode and returns a pandas DataFrame
    with the columns: url, url_mobile, title, seendate, socialimage, domain,
    language, sourcecountry.

    Params
    ------
    keyword
        The search keyword / phrase. Passed as an exact phrase match.
    timespan
        The timespan to search for, relative to the time of the request
        (eg. "30d" for the last 30 days). Must be one of the API's supported
        timespan formats (eg. "24h", "7d", "30d", "90d").
    max_records
        The maximum number of articles to return (up to 250).

    Returns
    -------
    pd.DataFrame
        DataFrame of matching articles, empty if nothing was found.
    """
    filters = Filters(keyword=keyword, timespan=timespan, num_records=max_records)
    _wait_for_rate_limit()
    gdelt = get_gdelt_client()
    return gdelt.article_search(filters)


def load_climate_timeline(
    mode: str = "timelinevol",
    keyword: str = DEFAULT_KEYWORD,
    timespan: str = DEFAULT_TIMESPAN,
) -> pd.DataFrame:
    """Fetch a coverage timeline for the given keyword from the GDELT DOC API.

    Params
    ------
    mode
        One of the API's timeline modes. Common options:
        "timelinevol" (volume of coverage as a percentage of total monitored
        coverage), "timelinevolraw" (actual article count), "timelinetone"
        (average tone of coverage), "timelinelang" (coverage by language),
        "timelinesourcecountry" (coverage by source country).
    keyword
        The search keyword / phrase.
    timespan
        The timespan to search for, relative to the time of the request.

    Returns
    -------
    pd.DataFrame
        DataFrame with a "datetime" column and one column per timeline
        series. Empty if no data was found.
    """
    filters = Filters(keyword=keyword, timespan=timespan, num_records=250)
    _wait_for_rate_limit()
    gdelt = get_gdelt_client()
    return gdelt.timeline_search(mode, filters)


def format_gdelt_date(seendate: Optional[str]) -> str:
    """Convert GDELT's seendate format (YYYYMMDDTHHMMSSZ) into a readable string."""
    if seendate is None or (isinstance(seendate, float) and pd.isna(seendate)):
        return "Unknown date"

    seendate = str(seendate)
    try:
        return (
            pd.to_datetime(seendate, format="%Y%m%dT%H%M%SZ", utc=True)
            .strftime("%Y-%m-%d %H:%M UTC")
        )
    except ValueError:
        return seendate
