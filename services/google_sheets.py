"""
services/google_sheets.py — Google Sheets API integration for Buddhiman Bharat.

Provides:
  - Voter feedback collection (anonymous civic survey)
  - Election result data sync from a public Google Sheet
  - Voter checklist completion tracking (opt-in)

Requires:
  - GOOGLE_SHEETS_KEY env var (API key with Sheets read access)
  - Or GOOGLE_SERVICE_ACCOUNT_JSON for write access (voter feedback)
"""

import json
import logging
import os
from typing import Optional
import requests

logger = logging.getLogger(__name__)

SHEETS_API_BASE = "https://sheets.googleapis.com/v4/spreadsheets"
GOOGLE_SHEETS_KEY: str = os.getenv("GOOGLE_SHEETS_KEY", "")
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")   # reuse Gemini key for Sheets read

# Public Sheets IDs (read-only, no auth needed with ?key=API_KEY)
PUBLIC_ELECTION_SHEET_ID = ""   # Set your Sheet ID here if you publish one
FEEDBACK_SHEET_ID = ""          # Set your feedback collection Sheet ID here

# ── Public Read (no OAuth needed) ────────────────────────────────────────────

def read_public_sheet(
    sheet_id: str,
    range_name: str = "Sheet1!A1:Z100",
    api_key: str = "",
) -> Optional[list[list]]:
    """
    Read rows from a publicly shared Google Sheet using API key.

    Args:
        sheet_id: The Sheets document ID from the URL.
        range_name: A1 notation range (e.g. 'Sheet1!A1:D50').
        api_key: Google API key with Sheets access.

    Returns:
        List of rows (each row is a list of cell values), or None on error.
    """
    key = api_key or GOOGLE_SHEETS_KEY or GOOGLE_API_KEY
    if not key or not sheet_id:
        logger.debug("Sheets read skipped — no API key or sheet ID")
        return None

    url = f"{SHEETS_API_BASE}/{sheet_id}/values/{range_name}"
    try:
        resp = requests.get(url, params={"key": key}, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        rows = data.get("values", [])
        logger.info("Sheets read OK: %d rows from %s", len(rows), sheet_id[:12])
        return rows
    except requests.RequestException as exc:
        logger.warning("Sheets read failed: %s", exc)
        return None


def append_feedback_row(
    name: str,
    state: str,
    rating: int,
    feedback: str,
    sheet_id: str = "",
) -> bool:
    """
    Append an anonymous voter feedback row to a Google Sheet via Apps Script webhook.
    (Direct append requires OAuth; this uses a published Apps Script Web App URL.)

    Set GOOGLE_SHEETS_WEBHOOK env var to your Apps Script deployment URL.

    Args:
        name: Voter's first name (optional, can be anonymous).
        state: State they're from.
        rating: 1–5 satisfaction rating.
        feedback: Free-text feedback.
        sheet_id: Target Sheet ID (overrides env var).

    Returns:
        True if successfully submitted.
    """
    webhook_url = os.getenv("GOOGLE_SHEETS_WEBHOOK", "")
    if not webhook_url:
        logger.debug("Feedback webhook not configured — skipping Sheets write")
        return False

    import re
    # Sanitise inputs before sending
    safe_name = re.sub(r"[^a-zA-Z\u0900-\u097F\s]", "", name.strip())[:50] or "Anonymous"
    safe_fb = re.sub(r"[<>\"';&]", "", feedback.strip())[:300]

    payload = {
        "name": safe_name,
        "state": state[:30],
        "rating": max(1, min(5, rating)),
        "feedback": safe_fb,
    }

    try:
        resp = requests.post(webhook_url, json=payload, timeout=8)
        if resp.status_code in (200, 201):
            logger.info("Feedback submitted to Sheets OK")
            return True
        logger.warning("Sheets webhook returned %d", resp.status_code)
    except requests.RequestException as exc:
        logger.warning("Sheets feedback failed: %s", exc)
    return False


def get_election_updates_from_sheet(sheet_id: str = "") -> list[dict]:
    """
    Read live election updates from a Google Sheet maintained by admins.
    Returns a list of update dicts with keys: title, body, state, timestamp.

    Sheet format (columns): Timestamp | State | Title | Body | Priority
    """
    sid = sheet_id or PUBLIC_ELECTION_SHEET_ID
    rows = read_public_sheet(sid, range_name="Updates!A2:E50")
    if not rows:
        return []

    updates = []
    for row in rows:
        if len(row) < 4:
            continue
        updates.append({
            "timestamp": row[0] if len(row) > 0 else "",
            "state":     row[1] if len(row) > 1 else "India",
            "title":     row[2] if len(row) > 2 else "",
            "body":      row[3] if len(row) > 3 else "",
            "priority":  row[4].lower() if len(row) > 4 else "normal",
        })
    return updates


def build_voter_feedback_form_url(prefill_state: str = "") -> str:
    """
    Return a Google Forms URL for anonymous voter feedback.
    Replace FORM_ID with your actual published Google Form ID.
    """
    form_id = os.getenv("GOOGLE_FORM_ID", "YOUR_FORM_ID_HERE")
    base = f"https://docs.google.com/forms/d/{form_id}/viewform"
    if prefill_state:
        encoded = requests.utils.quote(prefill_state)
        base += f"?usp=pp_url&entry.STATE_FIELD={encoded}"
    return base
