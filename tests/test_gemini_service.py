"""
tests/test_gemini_service.py — Tests for Gemini AI service layer.
"""

import inspect
import pytest
from unittest.mock import MagicMock, patch

from services.gemini_service import (
    detect_language_from_text,
    get_quick_answers,
    call_gemini,
    call_gemini_streaming,
    GREETING_MESSAGE,
    SYSTEM_PROMPT,
    _build_context,
)


# ── Language Detection ────────────────────────────────────────────────────────

class TestDetectLanguage:
    def test_english_default(self):
        assert detect_language_from_text("Hello, where is my booth?") == "en"

    def test_empty_returns_english(self):
        assert detect_language_from_text("") == "en"

    def test_none_returns_english(self):
        assert detect_language_from_text(None) == "en"

    def test_hindi_devanagari(self):
        assert detect_language_from_text("मेरा मतदान केंद्र कहाँ है?") == "hi"

    def test_bengali(self):
        assert detect_language_from_text("আমার ভোট কেন্দ্র কোথায়?") == "bn"

    def test_tamil(self):
        assert detect_language_from_text("என் வாக்குச் சாவடி எங்கே?") == "ta"

    def test_telugu(self):
        assert detect_language_from_text("నా పోలింగ్ బూత్ ఎక్కడ ఉంది?") == "te"

    def test_gujarati(self):
        assert detect_language_from_text("મારો મત બૂથ ક્યાં છે?") == "gu"

    def test_kannada(self):
        assert detect_language_from_text("ನನ್ನ ಮತದಾನ ಕೇಂದ್ರ ಎಲ್ಲಿದೆ?") == "kn"

    def test_malayalam(self):
        assert detect_language_from_text("എന്റെ വോട്ടിംഗ് ബൂത്ത് എവിടെ?") == "ml"

    def test_urdu(self):
        assert detect_language_from_text("میرا ووٹنگ بوتھ کہاں ہے؟") == "ur"

    def test_mixed_english_hindi_prefers_hindi(self):
        # Contains Devanagari — should be detected as Hindi
        assert detect_language_from_text("Please tell me about मतदान") == "hi"


# ── Quick Answers ─────────────────────────────────────────────────────────────

class TestGetQuickAnswers:
    def test_booth_query(self):
        r = get_quick_answers("Where is my polling booth?")
        assert r is not None
        assert "1950" in r

    def test_voter_id_query(self):
        r = get_quick_answers("How do I download my voter ID?")
        assert r is not None
        assert "nvsp.in" in r.lower() or "EPIC" in r

    def test_nota_query(self):
        r = get_quick_answers("What is NOTA?")
        assert r is not None
        assert "NOTA" in r

    def test_evm_query(self):
        r = get_quick_answers("Is EVM tamper-proof?")
        assert r is not None
        assert "EVM" in r

    def test_helpline_query(self):
        r = get_quick_answers("What is the election helpline?")
        assert r is not None
        assert "1950" in r

    def test_register_query(self):
        r = get_quick_answers("How to register as new voter?")
        assert r is not None
        assert "Form 6" in r or "register" in r.lower()

    def test_aadhaar_query(self):
        r = get_quick_answers("Is Aadhaar mandatory to vote?")
        assert r is not None
        assert "mandatory" in r.lower() or "NOT" in r

    def test_unrelated_returns_none(self):
        assert get_quick_answers("What is the capital of France?") is None

    def test_empty_returns_none(self):
        assert get_quick_answers("") is None

    def test_short_returns_none(self):
        assert get_quick_answers("hi") is None


# ── Context Builder ───────────────────────────────────────────────────────────

class TestBuildContext:
    def test_no_data_generic_context(self):
        ctx = _build_context(None, "", "en")
        assert "General" in ctx
        assert "en" in ctx

    def test_with_election_data(self):
        data = {
            "election_name": "Bihar Assembly 2025",
            "state": "Bihar",
            "upcoming": {},
        }
        ctx = _build_context(data, "BR", "hi")
        assert "Bihar" in ctx
        assert "BR" in ctx
        assert "hi" in ctx

    def test_missing_fields_graceful(self):
        ctx = _build_context({}, "XX", "en")
        assert isinstance(ctx, str)
        assert len(ctx) > 0


# ── call_gemini (no API key) ──────────────────────────────────────────────────

class TestCallGeminiNoKey:
    def test_returns_string_without_key(self):
        with patch("services.gemini_service.GOOGLE_API_KEY", ""):
            result = call_gemini("test", [], None, "", "en")
        assert isinstance(result, str)
        assert len(result) > 5

    def test_error_message_mentions_api_key(self):
        with patch("services.gemini_service.GOOGLE_API_KEY", ""):
            result = call_gemini("test", [], None, "", "en")
        assert "GOOGLE_API_KEY" in result or "AI" in result


# ── call_gemini_streaming (no API key) ───────────────────────────────────────

class TestCallGeminiStreaming:
    def test_returns_generator(self):
        gen = call_gemini_streaming("test", [], None, "", "en")
        assert inspect.isgenerator(gen)

    def test_yields_string_without_key(self):
        with patch("services.gemini_service.GOOGLE_API_KEY", ""):
            chunks = list(call_gemini_streaming("test", [], None, "", "en"))
        assert len(chunks) > 0
        full = "".join(chunks)
        assert isinstance(full, str)
        assert len(full) > 5

    def test_yields_warning_without_key(self):
        with patch("services.gemini_service.GOOGLE_API_KEY", ""):
            result = "".join(call_gemini_streaming("test", [], None, "", "en"))
        assert "GOOGLE_API_KEY" in result or "AI" in result or "Helpline" in result


# ── Constants ─────────────────────────────────────────────────────────────────

class TestConstants:
    def test_greeting_message_exists(self):
        assert GREETING_MESSAGE
        assert "Buddhiman Bharat" in GREETING_MESSAGE
        assert "1950" in GREETING_MESSAGE

    def test_system_prompt_has_context_placeholder(self):
        assert "{context}" in SYSTEM_PROMPT

    def test_system_prompt_mentions_non_partisan(self):
        assert "non-partisan" in SYSTEM_PROMPT.lower() or "neutral" in SYSTEM_PROMPT.lower()

    def test_system_prompt_mentions_eci(self):
        assert "1950" in SYSTEM_PROMPT or "ECI" in SYSTEM_PROMPT
