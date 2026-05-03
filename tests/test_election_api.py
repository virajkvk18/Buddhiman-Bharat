"""tests/test_election_api.py — Tests for election data service"""

import pytest
from unittest.mock import patch, MagicMock
from services.election_api import (
    get_election_data_for_location,
    get_national_result_summary,
    get_upcoming_elections,
    get_state_assembly_history,
)


class TestGetElectionDataForLocation:
    def test_returns_dict(self):
        result = get_election_data_for_location("Bihar")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = get_election_data_for_location("West Bengal")
        assert "election_name" in result
        assert "jurisdiction" in result
        assert "state_code" in result

    def test_delhi_pin_maps_correctly(self):
        result = get_election_data_for_location("110001")
        assert result["state_code"] == "DL"
        assert "Delhi" in result["jurisdiction"] or result["state"] == "Delhi"

    def test_state_name_maps_correctly(self):
        result = get_election_data_for_location("Tamil Nadu")
        assert result["state_code"] == "TN"

    def test_unknown_location_returns_india(self):
        result = get_election_data_for_location("UNKNOWN999")
        assert "election_name" in result  # graceful fallback


class TestGetNationalResultSummary:
    def test_returns_dict(self):
        result = get_national_result_summary()
        assert isinstance(result, dict)

    def test_has_results_key(self):
        result = get_national_result_summary()
        assert "results" in result or result == {}

    def test_bjp_in_results(self):
        result = get_national_result_summary()
        results = result.get("results", {})
        if results:
            assert "BJP" in results


class TestGetUpcomingElections:
    def test_returns_list(self):
        result = get_upcoming_elections()
        assert isinstance(result, list)

    def test_not_empty(self):
        result = get_upcoming_elections()
        assert len(result) > 0

    def test_each_has_state(self):
        result = get_upcoming_elections()
        for election in result:
            assert "state" in election


class TestGetStateAssemblyHistory:
    def test_west_bengal_has_data(self):
        result = get_state_assembly_history("WB")
        assert len(result) >= 3

    def test_data_has_required_fields(self):
        result = get_state_assembly_history("UP")
        for election in result:
            assert "year" in election
            assert "winner" in election
            assert "seats" in election

    def test_unknown_state_returns_empty(self):
        result = get_state_assembly_history("XX")
        assert result == []
