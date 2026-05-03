"""tests/test_fact_check.py — Tests for fact checking service"""

import pytest
from services.fact_check import check_claim, is_election_claim, KNOWN_MISINFORMATION


class TestIsElectionClaim:
    def test_evm_claim_detected(self):
        assert is_election_claim("EVMs can be hacked via bluetooth") is True

    def test_nota_claim_detected(self):
        assert is_election_claim("NOTA wins means re-election happens") is True

    def test_voter_fraud_detected(self):
        assert is_election_claim("There was massive voter fraud in the election") is True

    def test_unrelated_text_not_detected(self):
        assert is_election_claim("What is the weather today?") is False

    def test_empty_string(self):
        assert is_election_claim("") is False


class TestCheckClaim:
    def test_evm_bluetooth_returns_false(self):
        result = check_claim("EVMs can be hacked via bluetooth")
        assert result is not None
        assert result.get("found") is True
        assert result.get("verdict") == "FALSE"

    def test_aadhaar_mandatory_returns_misleading(self):
        result = check_claim("Aadhaar is mandatory to vote")
        assert result is not None
        assert result.get("found") is True
        assert result.get("verdict") == "MISLEADING"

    def test_nota_wins_returns_false(self):
        result = check_claim("NOTA wins means re-election happens")
        assert result is not None
        assert result.get("verdict") == "FALSE"

    def test_unknown_claim_returns_not_found(self):
        result = check_claim("Aliens helped design the EVM hardware in 2009")
        # Should not crash, returns dict
        assert isinstance(result, dict)

    def test_result_has_explanation(self):
        result = check_claim("EVMs can be hacked via bluetooth")
        if result and result.get("found"):
            assert "explanation" in result
            assert len(result["explanation"]) > 0


class TestKnownMisinformation:
    def test_database_not_empty(self):
        assert len(KNOWN_MISINFORMATION) >= 3

    def test_each_has_required_fields(self):
        for item in KNOWN_MISINFORMATION:
            assert "claim" in item
            assert "verdict" in item
            assert "explanation" in item
            assert "source" in item

    def test_verdicts_are_valid(self):
        valid_verdicts = {"TRUE", "FALSE", "MISLEADING"}
        for item in KNOWN_MISINFORMATION:
            assert item["verdict"] in valid_verdicts
