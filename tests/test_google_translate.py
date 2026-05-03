"""
tests/test_google_translate.py — Tests for Google Cloud Translation API service.
"""

import pytest
from unittest.mock import patch, MagicMock
from services.google_translate import (
    translate_text,
    detect_language,
    translate_election_notice,
    get_supported_languages,
    GOOGLE_TRANSLATE_CODES,
)


class TestTranslateText:
    def test_no_api_key_returns_none(self):
        with patch("services.google_translate.GOOGLE_API_KEY", ""):
            result = translate_text("Hello", "hi", api_key="")
        assert result is None

    def test_same_language_returns_original(self):
        result = translate_text("Hello", "en", "en", api_key="FAKE")
        assert result == "Hello"

    def test_empty_text_returns_empty(self):
        result = translate_text("", "hi", api_key="FAKE")
        assert result == ""

    def test_successful_translation(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "data": {"translations": [{"translatedText": "नमस्ते"}]}
        }
        mock_resp.raise_for_status = MagicMock()

        with patch("requests.post", return_value=mock_resp):
            result = translate_text("Hello", "hi", api_key="FAKE_KEY")

        assert result == "नमस्ते"

    def test_api_error_returns_none(self):
        import requests as _req
        with patch("requests.post", side_effect=_req.RequestException("timeout")):
            result = translate_text("Hello", "ta", api_key="FAKE")
        assert result is None

    def test_text_truncated_to_5000_chars(self):
        """Verify very long text is truncated before sending to API."""
        captured = {}
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": {"translations": [{"translatedText": "x"}]}}
        mock_resp.raise_for_status = MagicMock()

        def capture(url, params=None, json=None, timeout=None):
            captured["q"] = json.get("q", "")
            return mock_resp

        with patch("requests.post", side_effect=capture):
            translate_text("A" * 6000, "hi", api_key="FAKE")

        assert len(captured.get("q", "")) <= 5000


@pytest.mark.parametrize("lang_code,expected_google_code", [
    ("hi", "hi"),
    ("bn", "bn"),
    ("ta", "ta"),
    ("te", "te"),
    ("ml", "ml"),
    ("gu", "gu"),
    ("kn", "kn"),
    ("pa", "pa"),
    ("ur", "ur"),
    ("mr", "mr"),
])
def test_language_code_mapping(lang_code, expected_google_code):
    """All major Indian languages map to correct Google Translate BCP-47 codes."""
    assert GOOGLE_TRANSLATE_CODES[lang_code] == expected_google_code


class TestDetectLanguage:
    def test_no_key_returns_none(self):
        with patch("services.google_translate.GOOGLE_API_KEY", ""):
            result = detect_language("Hello world", api_key="")
        assert result is None

    def test_empty_text_returns_none(self):
        result = detect_language("", api_key="FAKE")
        assert result is None

    def test_successful_detection(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "data": {"detections": [[{"language": "hi", "confidence": 0.99}]]}
        }
        mock_resp.raise_for_status = MagicMock()

        with patch("requests.post", return_value=mock_resp):
            result = detect_language("नमस्ते", api_key="FAKE")

        assert result == "hi"

    def test_low_confidence_returns_none(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "data": {"detections": [[{"language": "hi", "confidence": 0.3}]]}
        }
        mock_resp.raise_for_status = MagicMock()

        with patch("requests.post", return_value=mock_resp):
            result = detect_language("abc", api_key="FAKE")

        assert result is None


class TestTranslateElectionNotice:
    def test_english_returns_unchanged(self):
        notice = "Polling will be held on June 1."
        result = translate_election_notice(notice, "en")
        assert result == notice

    def test_empty_target_returns_unchanged(self):
        notice = "Vote today."
        result = translate_election_notice(notice, "")
        assert result == notice

    def test_fallback_to_original_on_api_failure(self):
        with patch("services.google_translate.translate_text", return_value=None):
            result = translate_election_notice("Vote today.", "hi")
        assert result == "Vote today."

    def test_returns_translation_when_available(self):
        with patch("services.google_translate.translate_text", return_value="आज वोट करें।"):
            result = translate_election_notice("Vote today.", "hi")
        assert result == "आज वोट करें।"


class TestGetSupportedLanguages:
    def test_returns_list(self):
        langs = get_supported_languages()
        assert isinstance(langs, list)

    def test_not_empty(self):
        langs = get_supported_languages()
        assert len(langs) > 5

    def test_each_has_required_keys(self):
        for lang in get_supported_languages():
            assert "code" in lang
            assert "google_code" in lang
            assert "name" in lang

    def test_english_included(self):
        codes = [l["code"] for l in get_supported_languages()]
        assert "en" in codes

    def test_hindi_included(self):
        codes = [l["code"] for l in get_supported_languages()]
        assert "hi" in codes
