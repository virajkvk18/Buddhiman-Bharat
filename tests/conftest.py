"""
tests/conftest.py — Shared pytest fixtures for Buddhiman Bharat test suite.
"""

import pytest
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def sample_election_data() -> dict:
    """Return a realistic election data dict for Bihar."""
    return {
        "election_name": "Bihar Assembly Election 2025",
        "jurisdiction": "Bihar",
        "state": "Bihar",
        "state_code": "BR",
        "upcoming": {
            "state": "Bihar",
            "state_code": "BR",
            "type": "Assembly",
            "year": 2025,
            "seats": 243,
            "schedule": "November 2025",
            "status": "upcoming",
        },
        "recent_result": None,
        "pin": None,
        "location_type": "state",
    }


@pytest.fixture
def sample_delhi_data() -> dict:
    """Return election data for Delhi (PIN code scenario)."""
    return {
        "election_name": "Delhi Assembly Election 2026",
        "jurisdiction": "Delhi",
        "state": "Delhi",
        "state_code": "DL",
        "upcoming": {
            "state": "Delhi",
            "state_code": "DL",
            "type": "Assembly",
            "year": 2026,
            "seats": 70,
            "schedule": "February 2026",
            "status": "upcoming",
        },
        "recent_result": None,
        "pin": "110001",
        "location_type": "pin",
    }


@pytest.fixture
def sample_chat_history() -> list[dict]:
    """Return a multi-turn chat history for AI tests."""
    return [
        {"role": "user",      "content": "Where is my polling booth?"},
        {"role": "assistant", "content": "Visit voterportal.eci.gov.in to find your booth."},
        {"role": "user",      "content": "What documents do I need?"},
        {"role": "assistant", "content": "Any one of 12 valid photo IDs is accepted."},
    ]


@pytest.fixture
def mock_gemini_response() -> str:
    """Return a canned AI response string."""
    return (
        "To find your polling booth, visit **voterportal.eci.gov.in** "
        "and enter your EPIC number. You can also SMS your EPIC number to **1950**. "
        "ECI Helpline: **1950**"
    )


@pytest.fixture
def evm_myth_claim() -> str:
    return "EVMs can be hacked via bluetooth"


@pytest.fixture
def aadhaar_myth_claim() -> str:
    return "Aadhaar is mandatory to vote in India"


@pytest.fixture
def valid_pin_codes() -> list[str]:
    return ["110001", "400001", "700001", "600001", "500001", "302001"]


@pytest.fixture
def invalid_inputs() -> list[str]:
    return [
        "",
        "a",
        "<script>alert(1)</script>",
        "'; DROP TABLE voters; --",
        "A" * 101,
        "12345",    # 5-digit, not 6
        "1234567",  # 7-digit
    ]
