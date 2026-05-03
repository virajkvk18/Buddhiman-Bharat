"""
utils/location_utils.py — PIN code, state, and constituency detection for India
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# PIN code prefix to state mapping (first 2 digits)
PIN_TO_STATE = {
    "11": "DL",  # Delhi
    "12": "HR",  # Haryana
    "13": "HR",
    "14": "PB",  # Punjab
    "15": "PB",
    "16": "PB",
    "17": "HP",  # Himachal Pradesh
    "18": "JK",  # J&K
    "19": "JK",
    "20": "UP",  # Uttar Pradesh
    "21": "UP",
    "22": "UP",
    "23": "UP",
    "24": "UP",
    "25": "UP",
    "26": "UP",
    "27": "UP",
    "28": "UP",
    "30": "RJ",  # Rajasthan
    "31": "RJ",
    "32": "RJ",
    "33": "RJ",
    "34": "RJ",
    "36": "GJ",  # Gujarat
    "37": "GJ",
    "38": "GJ",
    "39": "GJ",
    "40": "MH",  # Maharashtra
    "41": "MH",
    "42": "MH",
    "43": "MH",
    "44": "MH",
    "45": "MP",  # Madhya Pradesh
    "46": "MP",
    "47": "MP",
    "48": "MP",
    "49": "MP",
    "50": "TS",  # Telangana
    "51": "TS",
    "52": "TS",
    "53": "AP",  # Andhra Pradesh
    "54": "AP",
    "55": "AP",
    "56": "KA",  # Karnataka
    "57": "KA",
    "58": "KA",
    "59": "KA",
    "60": "TN",  # Tamil Nadu
    "61": "TN",
    "62": "TN",
    "63": "TN",
    "64": "TN",
    "67": "KL",  # Kerala
    "68": "KL",
    "69": "KL",
    "70": "WB",  # West Bengal
    "71": "WB",
    "72": "WB",
    "73": "WB",
    "74": "WB",
    "75": "WB",
    "76": "WB",
    "77": "WB",
    "78": "AS",  # Assam
    "79": "AS",
    "80": "BR",  # Bihar
    "81": "BR",
    "82": "BR",
    "83": "BR",
    "84": "BR",
    "85": "JH",  # Jharkhand
    "82": "JH",
    "83": "JH",
    "75": "OD",  # Odisha
    "76": "OD",
    "77": "OD",
    "49": "CG",  # Chhattisgarh
    "48": "CG",
}

STATE_NAME_TO_CODE = {
    "andhra pradesh": "AP", "ap": "AP",
    "arunachal pradesh": "AR",
    "assam": "AS",
    "bihar": "BR",
    "chhattisgarh": "CG", "chattisgarh": "CG",
    "goa": "GA",
    "gujarat": "GJ",
    "haryana": "HR",
    "himachal pradesh": "HP",
    "jharkhand": "JH",
    "karnataka": "KA",
    "kerala": "KL",
    "madhya pradesh": "MP", "mp": "MP",
    "maharashtra": "MH",
    "manipur": "MN",
    "meghalaya": "ML",
    "mizoram": "MZ",
    "nagaland": "NL",
    "odisha": "OD", "orissa": "OD",
    "punjab": "PB",
    "rajasthan": "RJ",
    "sikkim": "SK",
    "tamil nadu": "TN", "tamilnadu": "TN",
    "telangana": "TS",
    "tripura": "TR",
    "uttar pradesh": "UP", "up": "UP",
    "uttarakhand": "UK", "uttaranchal": "UK",
    "west bengal": "WB",
    "andaman": "AN", "andaman and nicobar": "AN",
    "chandigarh": "CH",
    "dadra": "DN", "daman": "DN",
    "delhi": "DL", "new delhi": "DL",
    "jammu": "JK", "kashmir": "JK", "jammu and kashmir": "JK", "j&k": "JK",
    "ladakh": "LA",
    "lakshadweep": "LD",
    "puducherry": "PY", "pondicherry": "PY",
}


def parse_location(raw: str) -> dict:
    """Parse raw location input into structured data."""
    raw = raw.strip()
    normalized = raw.lower().strip()

    result = {
        "raw": raw,
        "normalized": normalized,
        "type": "unknown",
        "state_code": None,
        "pin": None,
    }

    # Check if PIN code (6-digit number)
    if re.match(r"^\d{6}$", raw):
        result["type"] = "pin"
        result["pin"] = raw
        prefix = raw[:2]
        result["state_code"] = PIN_TO_STATE.get(prefix)
        return result

    # Check if state name
    if normalized in STATE_NAME_TO_CODE:
        result["type"] = "state"
        result["state_code"] = STATE_NAME_TO_CODE[normalized]
        result["normalized"] = raw  # preserve original case
        return result

    # Fuzzy match state names
    for name, code in STATE_NAME_TO_CODE.items():
        if normalized in name or name in normalized:
            result["type"] = "state"
            result["state_code"] = code
            result["normalized"] = raw
            return result

    return result


def get_state_from_location(location: str) -> Optional[str]:
    """Return state code from location string."""
    parsed = parse_location(location)
    return parsed.get("state_code")


def sanitize_text(text: str) -> str:
    """Remove potentially dangerous HTML/script characters."""
    if not text:
        return ""
    sanitized = re.sub(r"[<>&\"']", lambda m: {
        "<": "&lt;", ">": "&gt;", "&": "&amp;",
        '"': "&quot;", "'": "&#x27;"
    }[m.group()], str(text))
    return sanitized[:500]  # hard length cap
