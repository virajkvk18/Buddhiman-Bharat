"""
services/fact_check.py — Google Fact Check Tools API integration
"""

import logging
import requests
from typing import Optional
from config.settings import FACT_CHECK_API_KEY

logger = logging.getLogger(__name__)

FACT_CHECK_API_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

# Common Indian election misinformation patterns
KNOWN_MISINFORMATION = [
    {
        "claim": "EVMs can be hacked via bluetooth",
        "verdict": "FALSE",
        "explanation": "EVMs are standalone devices with no wireless connectivity. The Supreme Court upheld their integrity in 2024.",
        "source": "Election Commission of India",
    },
    {
        "claim": "You need Aadhaar to vote",
        "verdict": "MISLEADING",
        "explanation": "Aadhaar is one of 12 accepted documents but NOT mandatory. Voter ID (EPIC) is sufficient.",
        "source": "ECI Guidelines",
    },
    {
        "claim": "NOTA wins means re-election",
        "verdict": "FALSE",
        "explanation": "If NOTA gets the most votes, the candidate with the next highest votes still wins. Re-election is NOT triggered.",
        "source": "Supreme Court Judgment 2013",
    },
    {
        "claim": "NRI votes cancel each other",
        "verdict": "FALSE",
        "explanation": "NRIs registered on Indian electoral rolls vote just like resident Indians — one vote per person.",
        "source": "Representation of the People Act 1951",
    },
]


def check_claim(query: str) -> Optional[dict]:
    """
    Check a claim against Google Fact Check API.
    Falls back to local database if API is unavailable.
    """
    # First check local database for known misinformation
    query_lower = query.lower()
    for item in KNOWN_MISINFORMATION:
        if any(word in query_lower for word in item["claim"].lower().split()[:3]):
            return {
                "found": True,
                "source": "local_db",
                "claim": item["claim"],
                "verdict": item["verdict"],
                "explanation": item["explanation"],
                "cited_source": item["source"],
            }

    # Try Google Fact Check API
    if not FACT_CHECK_API_KEY:
        return {"found": False, "source": "no_api_key"}

    try:
        params = {
            "query": query[:200],
            "key": FACT_CHECK_API_KEY,
            "languageCode": "en",
        }
        resp = requests.get(FACT_CHECK_API_URL, params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            claims = data.get("claims", [])
            if claims:
                first = claims[0]
                rating = first.get("claimReview", [{}])[0]
                return {
                    "found": True,
                    "source": "google_fact_check",
                    "claim": first.get("text", query),
                    "verdict": rating.get("textualRating", "Unverified"),
                    "explanation": rating.get("title", ""),
                    "cited_source": rating.get("publisher", {}).get("name", "Unknown"),
                    "url": rating.get("url", ""),
                }
    except Exception as exc:
        logger.debug("Fact Check API error: %s", exc)

    return {"found": False, "source": "not_found"}


def is_election_claim(text: str) -> bool:
    """Detect if text contains a factual election claim that should be fact-checked."""
    keywords = [
        "evm", "hack", "rigged", "cheat", "fake votes", "booth capturing",
        "nota wins", "aadhaar compulsory", "nri votes", "cancelled",
        "election postponed", "cancelled election", "voter fraud",
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)
