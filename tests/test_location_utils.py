"""tests/test_location_utils.py — Tests for location parsing"""

import pytest
from utils.location_utils import parse_location, get_state_from_location, sanitize_text


class TestParseLocation:
    def test_pin_code_delhi(self):
        result = parse_location("110001")
        assert result["type"] == "pin"
        assert result["state_code"] == "DL"
        assert result["pin"] == "110001"

    def test_pin_code_mumbai(self):
        result = parse_location("400001")
        assert result["type"] == "pin"
        assert result["state_code"] == "MH"

    def test_pin_code_kolkata(self):
        result = parse_location("700001")
        assert result["type"] == "pin"
        assert result["state_code"] == "WB"

    def test_state_name_exact(self):
        result = parse_location("Bihar")
        assert result["type"] == "state"
        assert result["state_code"] == "BR"

    def test_state_name_case_insensitive(self):
        result = parse_location("GUJARAT")
        assert result["state_code"] == "GJ"

    def test_state_name_with_spaces(self):
        result = parse_location("West Bengal")
        assert result["state_code"] == "WB"

    def test_state_abbreviation(self):
        result = parse_location("UP")
        assert result["state_code"] == "UP"

    def test_unknown_input(self):
        result = parse_location("XYZ123")
        assert result["state_code"] is None

    def test_sanitize_text_xss(self):
        result = sanitize_text("<script>alert(1)</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_sanitize_text_length_cap(self):
        long_text = "A" * 600
        assert len(sanitize_text(long_text)) <= 500

    def test_sanitize_empty(self):
        assert sanitize_text("") == ""
        assert sanitize_text(None) == ""


class TestGetStateFromLocation:
    def test_pin_returns_state(self):
        assert get_state_from_location("600001") == "TN"

    def test_state_name_returns_code(self):
        assert get_state_from_location("kerala") == "KL"

    def test_unknown_returns_none(self):
        assert get_state_from_location("ZZZZZZ") is None
