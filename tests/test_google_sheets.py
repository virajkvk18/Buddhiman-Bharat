"""
tests/test_google_sheets.py — Tests for services/google_sheets.py
"""

import pytest
from unittest.mock import patch, MagicMock
from services.google_sheets import (
    read_public_sheet,
    append_feedback_row,
    get_election_updates_from_sheet,
    build_voter_feedback_form_url,
)


class TestReadPublicSheet:
    def test_no_key_returns_none(self):
        with patch("services.google_sheets.GOOGLE_SHEETS_KEY", ""), \
             patch("services.google_sheets.GOOGLE_API_KEY", ""):
            result = read_public_sheet("FAKE_SHEET_ID")
        assert result is None

    def test_no_sheet_id_returns_none(self):
        result = read_public_sheet("")
        assert result is None

    def test_successful_read_returns_rows(self):
        mock_data = {"values": [["State", "Seats"], ["Bihar", "243"], ["Delhi", "70"]]}
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_data
        mock_resp.raise_for_status = MagicMock()

        with patch("services.google_sheets.GOOGLE_API_KEY", "FAKE_KEY"), \
             patch("requests.get", return_value=mock_resp):
            result = read_public_sheet("SHEET123", api_key="FAKE_KEY")

        assert result is not None
        assert len(result) == 3
        assert result[0] == ["State", "Seats"]

    def test_api_error_returns_none(self):
        import requests
        with patch("services.google_sheets.GOOGLE_API_KEY", "FAKE_KEY"), \
             patch("requests.get", side_effect=requests.RequestException("timeout")):
            result = read_public_sheet("SHEET123", api_key="FAKE_KEY")
        assert result is None


class TestAppendFeedbackRow:
    def test_no_webhook_returns_false(self):
        with patch.dict("os.environ", {"GOOGLE_SHEETS_WEBHOOK": ""}):
            result = append_feedback_row("Rahul", "Bihar", 5, "Great app!")
        assert result is False

    def test_successful_post_returns_true(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200

        with patch.dict("os.environ", {"GOOGLE_SHEETS_WEBHOOK": "https://script.google.com/fake"}), \
             patch("requests.post", return_value=mock_resp):
            result = append_feedback_row("Priya", "Delhi", 4, "Very helpful!")
        assert result is True

    def test_bad_status_returns_false(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 500

        with patch.dict("os.environ", {"GOOGLE_SHEETS_WEBHOOK": "https://script.google.com/fake"}), \
             patch("requests.post", return_value=mock_resp):
            result = append_feedback_row("Test", "UP", 3, "OK")
        assert result is False

    def test_rating_clamped_to_1_5(self):
        """Verify that rating values outside 1-5 are clamped."""
        captured = {}
        mock_resp = MagicMock()
        mock_resp.status_code = 200

        def capture_post(url, json=None, timeout=None):
            captured["rating"] = json.get("rating")
            return mock_resp

        with patch.dict("os.environ", {"GOOGLE_SHEETS_WEBHOOK": "https://script.google.com/fake"}), \
             patch("requests.post", side_effect=capture_post):
            append_feedback_row("Test", "UP", 10, "Test")  # 10 should be clamped to 5
        assert captured.get("rating") == 5

    def test_xss_stripped_from_feedback(self):
        captured = {}
        mock_resp = MagicMock()
        mock_resp.status_code = 200

        def capture_post(url, json=None, timeout=None):
            captured["feedback"] = json.get("feedback", "")
            return mock_resp

        with patch.dict("os.environ", {"GOOGLE_SHEETS_WEBHOOK": "https://script.google.com/fake"}), \
             patch("requests.post", side_effect=capture_post):
            append_feedback_row("Test", "KA", 3, "<script>alert(1)</script>Nice app")
        assert "<script>" not in captured.get("feedback", "")


class TestGetElectionUpdates:
    def test_empty_sheet_returns_empty_list(self):
        with patch("services.google_sheets.read_public_sheet", return_value=None):
            result = get_election_updates_from_sheet("FAKE")
        assert result == []

    def test_parses_rows_correctly(self):
        fake_rows = [
            ["2025-05-01", "Bihar", "Nomination filing begins", "Candidates can file from May 1", "high"],
            ["2025-05-10", "India", "MCC activated", "Model Code of Conduct now in force", "normal"],
        ]
        with patch("services.google_sheets.read_public_sheet", return_value=fake_rows):
            result = get_election_updates_from_sheet("FAKE")

        assert len(result) == 2
        assert result[0]["state"] == "Bihar"
        assert result[0]["title"] == "Nomination filing begins"
        assert result[0]["priority"] == "high"

    def test_short_rows_handled_gracefully(self):
        fake_rows = [["2025-01-01"]]  # Only 1 column
        with patch("services.google_sheets.read_public_sheet", return_value=fake_rows):
            result = get_election_updates_from_sheet("FAKE")
        assert result == []  # Row too short, skipped


class TestBuildVoterFeedbackFormUrl:
    def test_returns_string(self):
        url = build_voter_feedback_form_url()
        assert isinstance(url, str)
        assert "google.com/forms" in url

    def test_state_prefill_appended(self):
        url = build_voter_feedback_form_url("Bihar")
        assert "Bihar" in url or "usp" in url
