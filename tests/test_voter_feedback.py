"""
tests/test_voter_feedback.py — Tests for voter feedback + Google Sheets notifications.
"""

import pytest
from unittest.mock import patch


class TestVoterFeedbackIntegration:
    """Test the feedback→Sheets pipeline without Streamlit."""

    def test_feedback_submitted_to_sheets(self):
        """Valid feedback triggers Sheets append call."""
        from services.google_sheets import append_feedback_row
        mock_resp_obj = type("R", (), {"status_code": 200})()
        with patch.dict("os.environ", {"GOOGLE_SHEETS_WEBHOOK": "https://script.google.com/fake"}), \
             patch("requests.post", return_value=mock_resp_obj):
            result = append_feedback_row("Priya", "Bihar", 5, "Very helpful!")
        assert result is True

    def test_xss_not_stored_in_sheets(self):
        """XSS payloads are stripped before reaching Sheets."""
        captured = {}
        mock_resp = type("R", (), {"status_code": 200})()

        def capture(url, json=None, timeout=None):
            captured.update(json or {})
            return mock_resp

        with patch.dict("os.environ", {"GOOGLE_SHEETS_WEBHOOK": "https://script.google.com/fake"}), \
             patch("requests.post", side_effect=capture):
            append_feedback_row("Test", "UP", 3, "<script>evil()</script>Nice!")

        assert "<script>" not in captured.get("feedback", "")

    def test_rating_out_of_range_clamped(self):
        """Ratings outside 1–5 are clamped."""
        captured = {}
        mock_resp = type("R", (), {"status_code": 200})()

        def capture(url, json=None, timeout=None):
            captured.update(json or {})
            return mock_resp

        with patch.dict("os.environ", {"GOOGLE_SHEETS_WEBHOOK": "https://script.google.com/fake"}), \
             patch("requests.post", side_effect=capture):
            append_feedback_row("Test", "DL", 0, "Test feedback here")

        assert captured.get("rating", 0) >= 1

    @pytest.mark.parametrize("state,rating,feedback", [
        ("Bihar",       5, "Excellent — helped me find my booth!"),
        ("Delhi",       4, "Good app, needs Tamil support improvement"),
        ("West Bengal", 3, "আমার বুথ খুঁজতে সাহায্য করেছে"),
        ("Tamil Nadu",  5, "மிகவும் பயனுள்ளது"),
    ])
    def test_feedback_accepted_for_all_states(self, state, rating, feedback):
        """Feedback is accepted and stored for voters from any state."""
        mock_resp = type("R", (), {"status_code": 200})()
        with patch.dict("os.environ", {"GOOGLE_SHEETS_WEBHOOK": "https://script.google.com/fake"}), \
             patch("requests.post", return_value=mock_resp):
            result = append_feedback_row("Voter", state, rating, feedback)
        assert result is True


class TestElectionNotifications:
    def test_empty_updates_on_no_sheet(self):
        """Returns empty list gracefully when sheet not configured."""
        from services.google_sheets import get_election_updates_from_sheet
        with patch("services.google_sheets.read_public_sheet", return_value=None):
            result = get_election_updates_from_sheet("")
        assert result == []

    def test_high_priority_update_parsed(self):
        """High priority updates are correctly flagged."""
        from services.google_sheets import get_election_updates_from_sheet
        fake = [["2025-06-01", "Bihar", "Phase 1 voting begins", "Go vote!", "high"]]
        with patch("services.google_sheets.read_public_sheet", return_value=fake):
            updates = get_election_updates_from_sheet("X")
        assert updates[0]["priority"] == "high"

    @pytest.mark.parametrize("row,should_parse", [
        (["2025-01-01", "India", "ECI Notice", "Content here", "normal"], True),
        (["2025-01-01"],                                                    False),  # too short
        (["2025-01-01", "Bihar"],                                           False),  # too short
        (["2025-01-01", "DL", "Title", "Body"],                             True),   # 4 cols OK
    ])
    def test_row_parsing_edge_cases(self, row, should_parse):
        """Rows are only parsed if they have >= 4 columns."""
        from services.google_sheets import get_election_updates_from_sheet
        with patch("services.google_sheets.read_public_sheet", return_value=[row]):
            result = get_election_updates_from_sheet("X")
        if should_parse:
            assert len(result) == 1
        else:
            assert len(result) == 0
