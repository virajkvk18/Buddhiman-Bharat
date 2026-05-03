"""
utils/validators.py — Input validation + rate limiting for Buddhiman Bharat.

Security hardening:
  - Location and query sanitisation
  - Prompt injection detection
  - Per-session rate limiting
  - Input length enforcement
"""

import re
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
MAX_INPUT_LENGTH: int = 100
MIN_QUERY_LENGTH: int = 2
MAX_QUERY_LENGTH: int = 500
RATE_LIMIT_WINDOW: int = 60          # seconds
RATE_LIMIT_MAX_CALLS: int = 20       # max calls per window per session key

VALID_STATE_NAMES: frozenset[str] = frozenset({
    "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh",
    "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka",
    "kerala", "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram",
    "nagaland", "odisha", "orissa", "punjab", "rajasthan", "sikkim", "tamil nadu",
    "tamilnadu", "telangana", "tripura", "uttar pradesh", "uttarakhand",
    "west bengal", "andaman", "chandigarh", "dadra", "daman", "delhi",
    "jammu", "kashmir", "ladakh", "lakshadweep", "puducherry", "pondicherry",
    "ap", "up", "mp", "j&k", "wb", "new delhi", "uttaranchal", "chattisgarh",
    "jammu and kashmir", "andaman and nicobar", "jammu & kashmir", "india",
})

# Prompt injection patterns (case-insensitive)
_INJECTION_PATTERNS: tuple[str, ...] = (
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"you\s+are\s+now\s+(a|an|the)",
    r"act\s+as\s+(a|an)\s+(?!voter|citizen|indian|helpful)",
    r"jailbreak",
    r"\bDAN\s+mode\b",
    r"disregard\s+(all\s+)?previous",
    r"new\s+persona",
    r"system\s+prompt\s*(is|=|:)",
    r"<\|.*?\|>",                       # token injection
    r"\[INST\]",                        # LLaMA-style injection
)
_COMPILED_INJECTIONS = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]

# Simple in-process rate-limit store: session_key → [timestamps]
_rate_store: dict[str, list[float]] = {}


# ── Rate Limiting ─────────────────────────────────────────────────────────────

def check_rate_limit(session_key: str) -> tuple[bool, int]:
    """
    Check if session_key is within the allowed rate limit.

    Returns:
        (is_allowed, remaining_calls)
    """
    now = time.monotonic()
    calls = _rate_store.get(session_key, [])
    # Drop old calls outside window
    calls = [t for t in calls if now - t < RATE_LIMIT_WINDOW]

    if len(calls) >= RATE_LIMIT_MAX_CALLS:
        logger.warning("Rate limit exceeded for session: %s", session_key[:16])
        return False, 0

    calls.append(now)
    _rate_store[session_key] = calls
    remaining = RATE_LIMIT_MAX_CALLS - len(calls)
    return True, remaining


def reset_rate_limit(session_key: str) -> None:
    """Clear rate limit for a session (e.g. on new session start)."""
    _rate_store.pop(session_key, None)


# ── Location Input ────────────────────────────────────────────────────────────

def validate_location_input(text: str) -> bool:
    """
    Returns True if input is a valid Indian PIN code or known state/city name.

    Accepts:
      - Exactly 6-digit numeric strings (Indian PIN codes)
      - Known state names (exact or close match)
      - Alphanumeric + spaces + hyphens (constituency names)

    Rejects:
      - Empty / None / non-string
      - Input with HTML/script injection characters
      - Too short (< 2 chars) or too long (> MAX_INPUT_LENGTH)
    """
    if not text or not isinstance(text, str):
        return False

    text = text.strip()

    if len(text) > MAX_INPUT_LENGTH:
        logger.warning("Location input too long: %d chars", len(text))
        return False

    if len(text) < MIN_QUERY_LENGTH:
        return False

    if re.search(r"[<>\"';&{}\\]", text):
        logger.warning("Potential injection in location input: %s", text[:50])
        return False

    if re.match(r"^\d{6}$", text):
        return True

    lower = text.lower().strip()
    if lower in VALID_STATE_NAMES:
        return True

    # Allow unicode word characters + spaces + hyphens (city/district names)
    if re.match(r"^[\w\u0900-\u097F\u0980-\u09FF\u0C00-\u0D7F\s\-\.]+$", text, re.UNICODE) and len(text) >= 3:
        return True

    return False


# ── AI Query ─────────────────────────────────────────────────────────────────

def validate_ai_query(query: str) -> tuple[bool, str]:
    """
    Validate and sanitise an AI chat query.

    Returns:
        (is_valid: bool, sanitized_query: str)
    """
    if not query or not isinstance(query, str):
        return False, ""

    query = query.strip()

    if len(query) < MIN_QUERY_LENGTH:
        return False, ""

    # Truncate overlength queries
    if len(query) > MAX_QUERY_LENGTH:
        query = query[:MAX_QUERY_LENGTH]

    # Prompt injection detection
    for pattern in _COMPILED_INJECTIONS:
        if pattern.search(query):
            logger.warning("Prompt injection attempt blocked: %s", query[:60])
            return False, ""

    # Strip HTML tags
    sanitized = re.sub(r"<[^>]+>", "", query)

    # Remove null bytes and control characters (except newlines/tabs)
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", sanitized)

    return True, sanitized.strip()


# ── Feedback Input ────────────────────────────────────────────────────────────

def validate_feedback(text: str, max_len: int = 300) -> tuple[bool, str]:
    """Validate and sanitise voter feedback text."""
    if not text or not isinstance(text, str):
        return False, ""
    text = text.strip()
    if len(text) < 2:
        return False, ""
    # Strip HTML
    sanitized = re.sub(r"<[^>]+>", "", text)
    sanitized = re.sub(r"[;&{}\\]", "", sanitized)
    return True, sanitized[:max_len]


def is_safe_url(url: str) -> bool:
    """
    Minimal URL safety check — ensure it's an https link to a known safe domain.
    Used before rendering any external link fetched from APIs.
    """
    if not url or not isinstance(url, str):
        return False
    safe_domains = (
        "eci.gov.in", "nvsp.in", "voterportal.eci.gov.in",
        "results.eci.gov.in", "sveep.eci.gov.in", "cvigil.eci.gov.in",
        "google.com", "maps.google.com", "factchecktools.googleapis.com",
        "huggingface.co",
    )
    lower = url.lower()
    if not lower.startswith("https://"):
        return False
    return any(domain in lower for domain in safe_domains)
