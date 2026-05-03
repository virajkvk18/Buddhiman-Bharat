"""
services/election_api.py — Election data fetching and processing
"""

import json
import logging
import os
import requests
from typing import Optional
from datetime import datetime

from config.settings import STATES, UPCOMING_ELECTIONS, PARTIES
from utils.location_utils import parse_location
from utils.cache import cached, TTL_ELECTION_DATA

logger = logging.getLogger(__name__)

_DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "elections_2024_2026.json")


def _load_local_data() -> dict:
    """Load local election data JSON."""
    try:
        with open(_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.error("Failed to load local election data: %s", exc)
        return {}


@cached(ttl=TTL_ELECTION_DATA)
def get_election_data_for_location(location: str) -> dict:
    """
    Return election data dict for a given location string.
    Falls back gracefully to national data.
    """
    parsed = parse_location(location)
    state_code = parsed.get("state_code") or "IN"
    state_name = STATES.get(state_code, "India")

    local = _load_local_data()

    # Find upcoming election for this state
    upcoming = None
    for election in UPCOMING_ELECTIONS:
        if election["state_code"] == state_code:
            upcoming = election
            break

    # Find recent assembly result
    recent_result = None
    for result in local.get("assembly_elections_2024", []):
        if result.get("state_code") == state_code:
            recent_result = result
            break

    return {
        "election_name": (
            upcoming["state"] + f" Assembly Election {upcoming.get('year', 2026)}"
            if upcoming else "18th Lok Sabha (2024)"
        ),
        "jurisdiction": state_name,
        "state": state_name,
        "state_code": state_code,
        "upcoming": upcoming,
        "recent_result": recent_result,
        "general_2024": local.get("general_election_2024", {}),
        "pin": parsed.get("pin"),
        "location_type": parsed.get("type"),
    }


@cached(ttl=TTL_ELECTION_DATA)
def get_national_result_summary() -> dict:
    """Return 2024 Lok Sabha result summary."""
    data = _load_local_data()
    return data.get("general_election_2024", {})


def get_upcoming_elections() -> list:
    """Return all upcoming elections."""
    data = _load_local_data()
    return data.get("upcoming_elections_2025_2026", UPCOMING_ELECTIONS)


def get_state_assembly_history(state_code: str) -> list:
    """Return mock historical assembly election results for trend analysis."""
    # Realistic historical data for major states
    history_db = {
        "WB": [
            {"year": 2011, "winner": "TMC", "seats": 184, "total": 294, "turnout": 84.3},
            {"year": 2016, "winner": "TMC", "seats": 211, "total": 294, "turnout": 84.7},
            {"year": 2021, "winner": "TMC", "seats": 213, "total": 294, "turnout": 81.9},
        ],
        "UP": [
            {"year": 2012, "winner": "SP", "seats": 224, "total": 403, "turnout": 61.0},
            {"year": 2017, "winner": "BJP", "seats": 312, "total": 403, "turnout": 61.0},
            {"year": 2022, "winner": "BJP", "seats": 255, "total": 403, "turnout": 60.5},
        ],
        "MH": [
            {"year": 2014, "winner": "BJP", "seats": 122, "total": 288, "turnout": 63.4},
            {"year": 2019, "winner": "BJP+SS", "seats": 161, "total": 288, "turnout": 61.4},
            {"year": 2024, "winner": "Mahayuti", "seats": 230, "total": 288, "turnout": 66.1},
        ],
        "TN": [
            {"year": 2011, "winner": "AIADMK", "seats": 150, "total": 234, "turnout": 77.6},
            {"year": 2016, "winner": "AIADMK", "seats": 136, "total": 234, "turnout": 74.0},
            {"year": 2021, "winner": "DMK", "seats": 159, "total": 234, "turnout": 74.3},
        ],
        "GJ": [
            {"year": 2012, "winner": "BJP", "seats": 115, "total": 182, "turnout": 71.3},
            {"year": 2017, "winner": "BJP", "seats": 99, "total": 182, "turnout": 68.4},
            {"year": 2022, "winner": "BJP", "seats": 156, "total": 182, "turnout": 64.3},
        ],
        "RJ": [
            {"year": 2013, "winner": "BJP", "seats": 163, "total": 200, "turnout": 75.2},
            {"year": 2018, "winner": "INC", "seats": 100, "total": 200, "turnout": 74.7},
            {"year": 2023, "winner": "BJP", "seats": 115, "total": 200, "turnout": 75.8},
        ],
        "KA": [
            {"year": 2013, "winner": "INC", "seats": 122, "total": 224, "turnout": 71.8},
            {"year": 2018, "winner": "INC", "seats": 80, "total": 224, "turnout": 72.1},
            {"year": 2023, "winner": "INC", "seats": 135, "total": 224, "turnout": 73.2},
        ],
    }
    return history_db.get(state_code, [])


def fetch_eci_live_results(state_code: str) -> Optional[dict]:
    """
    Attempt to scrape live results from ECI portal.
    Returns None if unavailable (graceful degradation).
    """
    try:
        url = f"https://results.eci.gov.in/AcResultByState{state_code}.htm"
        headers = {"User-Agent": "BuddhimanBharat/1.0 (civic education; contact@example.com)"}
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            return {"raw_html": resp.text[:2000], "fetched_at": datetime.now().isoformat()}
    except requests.RequestException as exc:
        logger.debug("ECI live fetch failed (expected in demo): %s", exc)
    return None
