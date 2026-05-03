"""
services/google_translate.py — Google Cloud Translation API v2 integration.

Provides machine translation for election content into any of India's
22 scheduled languages when the Gemini AI is unavailable or for
static UI strings that are not yet hand-translated.

Uses the Google Cloud Translation API (Basic / v2):
  https://cloud.google.com/translate/docs/reference/rest

The GOOGLE_API_KEY (same key used for Gemini) also works for Translation
if the Translation API is enabled in Google Cloud Console.
"""

import logging
import requests
from typing import Optional
from config.settings import GOOGLE_API_KEY as _DEFAULT_API_KEY
from utils.cache import cached, TTL_FACT_CHECK

logger = logging.getLogger(__name__)

# Module-level key — can be overridden in tests via patch("services.google_translate._DEFAULT_API_KEY","")
_TRANSLATE_URL = "https://translation.googleapis.com/language/translate/v2"
_DETECT_URL    = "https://translation.googleapis.com/language/translate/v2/detect"

# BCP-47 language codes supported by Google Translate for Indian languages
GOOGLE_TRANSLATE_CODES: dict[str, str] = {
    "en":  "en",
    "hi":  "hi",
    "bn":  "bn",
    "te":  "te",
    "mr":  "mr",
    "ta":  "ta",
    "gu":  "gu",
    "kn":  "kn",
    "ml":  "ml",
    "pa":  "pa",
    "or":  "or",
    "as":  "as",
    "ur":  "ur",
    "mai": "mai",
    "bho": "bho",
    "raj": "raj",
    "sa":  "sa",    # Sanskrit
    "ne":  "ne",    # Nepali
    "kok": "kok",   # Konkani
    "doi": "doi",   # Dogri
    "mni": "mni",   # Manipuri
    "sd":  "sd",    # Sindhi
}


@cached(ttl=TTL_FACT_CHECK)
def translate_text(
    text: str,
    target_language: str,
    source_language: str = "en",
    api_key: str = "",
) -> Optional[str]:
    """
    Translate text using Google Cloud Translation API v2.

    Args:
        text: Source text to translate (max 5000 chars).
        target_language: BCP-47 language code (e.g. 'hi', 'ta', 'bn').
        source_language: Source language code (default 'en').
        api_key: Google API key with Translation API enabled.

    Returns:
        Translated string, or None if translation failed / unavailable.

    Example::

        translated = translate_text(
            "Your voter ID is required to vote.",
            target_language="hi"
        )
        # Returns: "मतदान के लिए आपकी वोटर आईडी आवश्यक है।"
    """
    if not api_key:
        api_key = _DEFAULT_API_KEY

    if not api_key:
        logger.debug("Translation skipped — no API key")
        return None

    if not text or not text.strip():
        return text

    if target_language == source_language:
        return text  # no-op

    # Map our internal lang code to Google BCP-47
    google_target = GOOGLE_TRANSLATE_CODES.get(target_language, target_language)
    google_source = GOOGLE_TRANSLATE_CODES.get(source_language, source_language)

    try:
        resp = requests.post(
            _TRANSLATE_URL,
            params={"key": api_key},
            json={
                "q": text[:5000],
                "source": google_source,
                "target": google_target,
                "format": "text",
            },
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json()
        translations = data.get("data", {}).get("translations", [])
        if translations:
            translated = translations[0].get("translatedText", "")
            logger.debug("Translated %d chars → %s", len(text), google_target)
            return translated
    except requests.RequestException as exc:
        logger.warning("Translation API error: %s", exc)
    except (KeyError, IndexError) as exc:
        logger.warning("Translation response parse error: %s", exc)

    return None


def detect_language(text: str, api_key: str = "") -> Optional[str]:
    """
    Detect the language of a text string via Google Cloud Translation API.

    Args:
        text: Text to detect language for.
        api_key: Google API key.

    Returns:
        BCP-47 language code string (e.g. 'hi', 'ta'), or None on failure.

    Note: For performance, prefer ``gemini_service.detect_language_from_text``
    (regex-based, zero latency) for chat input. Use this for longer documents.
    """
    if not api_key:
        api_key = _DEFAULT_API_KEY

    if not api_key or not text:
        return None

    try:
        resp = requests.post(
            _DETECT_URL,
            params={"key": api_key},
            json={"q": text[:500]},
            timeout=6,
        )
        resp.raise_for_status()
        data = resp.json()
        detections = data.get("data", {}).get("detections", [[]])
        if detections and detections[0]:
            lang = detections[0][0].get("language", "")
            confidence = detections[0][0].get("confidence", 0)
            logger.debug("Detected language: %s (confidence=%.2f)", lang, confidence)
            return lang if confidence > 0.5 else None
    except Exception as exc:
        logger.warning("Language detection failed: %s", exc)

    return None


def translate_election_notice(
    notice: str,
    target_language: str,
    api_key: str = "",
) -> str:
    """
    Translate an ECI election notice to the target language.
    Returns original text if translation unavailable.

    Args:
        notice: English election notice text.
        target_language: Target language code.
        api_key: Google API key.

    Returns:
        Translated notice string, falling back to original if API unavailable.
    """
    if target_language in ("en", ""):
        return notice

    translated = translate_text(notice, target_language, "en", api_key)
    return translated if translated else notice


def get_supported_languages() -> list[dict]:
    """
    Return list of supported Indian languages with their Google Translate codes.

    Returns:
        List of dicts with keys: code, google_code, name.
    """
    from config.settings import LANGUAGES
    return [
        {
            "code": code,
            "google_code": GOOGLE_TRANSLATE_CODES.get(code, code),
            "name": name,
        }
        for code, name in LANGUAGES.items()
        if code in GOOGLE_TRANSLATE_CODES
    ]
