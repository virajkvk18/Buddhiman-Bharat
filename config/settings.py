"""
config/settings.py — Centralised configuration for Buddhiman Bharat
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API Keys ─────────────────────────────────────────────────────────────────
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_MAPS_KEY: str = os.getenv("GOOGLE_MAPS_KEY", "")
FACT_CHECK_API_KEY: str = os.getenv("FACT_CHECK_API_KEY", "")
GOOGLE_SHEETS_KEY: str = os.getenv("GOOGLE_SHEETS_KEY", "")

# ── Gemini Model Config ───────────────────────────────────────────────────────
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_MAX_TOKENS: int = 512
MAX_AI_QUERIES: int = int(os.getenv("MAX_AI_QUERIES_PER_SESSION", "30"))

# ── India-specific Constants ──────────────────────────────────────────────────
INDIA = {
    "VOTER_HELPLINE": "1950",
    "ECI_WEBSITE": "https://eci.gov.in",
    "NVSP_URL": "https://nvsp.in",
    "VOTER_PORTAL": "https://voterportal.eci.gov.in",
    "ECI_RESULTS": "https://results.eci.gov.in",
    "SVEEP_URL": "https://sveep.eci.gov.in",
}

# ── Supported Indian Languages ────────────────────────────────────────────────
LANGUAGES = {
    "en": "English",
    "hi": "हिंदी",
    "bn": "বাংলা",
    "te": "తెలుగు",
    "mr": "मराठी",
    "ta": "தமிழ்",
    "gu": "ગુજરાતી",
    "kn": "ಕನ್ನಡ",
    "ml": "മലയാളം",
    "pa": "ਪੰਜਾਬੀ",
    "or": "ଓଡ଼ିଆ",
    "as": "অসমীয়া",
    "ur": "اردو",
    "mai": "मैथिली",
    "bho": "भोजपुरी",
    "raj": "राजस्थानी",
}

# ── Indian States & UTs ───────────────────────────────────────────────────────
STATES = {
    "AP": "Andhra Pradesh",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CG": "Chhattisgarh",
    "GA": "Goa",
    "GJ": "Gujarat",
    "HR": "Haryana",
    "HP": "Himachal Pradesh",
    "JH": "Jharkhand",
    "KA": "Karnataka",
    "KL": "Kerala",
    "MP": "Madhya Pradesh",
    "MH": "Maharashtra",
    "MN": "Manipur",
    "ML": "Meghalaya",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "OD": "Odisha",
    "PB": "Punjab",
    "RJ": "Rajasthan",
    "SK": "Sikkim",
    "TN": "Tamil Nadu",
    "TS": "Telangana",
    "TR": "Tripura",
    "UP": "Uttar Pradesh",
    "UK": "Uttarakhand",
    "WB": "West Bengal",
    "AN": "Andaman & Nicobar Islands",
    "CH": "Chandigarh",
    "DN": "Dadra & Nagar Haveli and Daman & Diu",
    "DL": "Delhi",
    "JK": "Jammu & Kashmir",
    "LA": "Ladakh",
    "LD": "Lakshadweep",
    "PY": "Puducherry",
}

# Major political parties
PARTIES = {
    "BJP": {"name": "Bharatiya Janata Party", "color": "#FF6B00", "symbol": "🪷"},
    "INC": {"name": "Indian National Congress", "color": "#00A3E0", "symbol": "✋"},
    "AAP": {"name": "Aam Aadmi Party", "color": "#00A5E0", "symbol": "🧹"},
    "SP": {"name": "Samajwadi Party", "color": "#FF0000", "symbol": "🚲"},
    "BSP": {"name": "Bahujan Samaj Party", "color": "#1E90FF", "symbol": "🐘"},
    "TMC": {"name": "All India Trinamool Congress", "color": "#29ABE2", "symbol": "🌸"},
    "DMK": {"name": "Dravida Munnetra Kazhagam", "color": "#CC0000", "symbol": "🌅"},
    "NCP": {"name": "Nationalist Congress Party", "color": "#00A3E0", "symbol": "⏰"},
    "SS": {"name": "Shiv Sena", "color": "#FF8C00", "symbol": "🏹"},
    "CPI-M": {"name": "Communist Party of India (Marxist)", "color": "#CC0000", "symbol": "⚒️"},
    "TDP": {"name": "Telugu Desam Party", "color": "#FFFF00", "symbol": "🚲"},
    "JDU": {"name": "Janata Dal (United)", "color": "#00A86B", "symbol": "🏹"},
    "RJD": {"name": "Rashtriya Janata Dal", "color": "#006400", "symbol": "🔦"},
    "YSRCP": {"name": "YSR Congress Party", "color": "#00BFFF", "symbol": "🏠"},
    "BRS": {"name": "Bharat Rashtra Samithi", "color": "#FF69B4", "symbol": "🚗"},
}

# ── Upcoming Elections 2025–2026 ──────────────────────────────────────────────
UPCOMING_ELECTIONS = [
    {
        "state": "Bihar",
        "state_code": "BR",
        "type": "Assembly",
        "year": 2025,
        "seats": 243,
        "schedule": "November 2025",
        "status": "upcoming",
    },
    {
        "state": "Delhi",
        "state_code": "DL",
        "type": "Assembly",
        "year": 2026,
        "seats": 70,
        "schedule": "February 2026",
        "status": "upcoming",
    },
    {
        "state": "West Bengal",
        "state_code": "WB",
        "type": "Assembly",
        "year": 2026,
        "seats": 294,
        "schedule": "April–May 2026",
        "status": "upcoming",
    },
    {
        "state": "Tamil Nadu",
        "state_code": "TN",
        "type": "Assembly",
        "year": 2026,
        "seats": 234,
        "schedule": "April 2026",
        "status": "upcoming",
    },
    {
        "state": "Kerala",
        "state_code": "KL",
        "type": "Assembly",
        "year": 2026,
        "seats": 140,
        "schedule": "April 2026",
        "status": "upcoming",
    },
    {
        "state": "Assam",
        "state_code": "AS",
        "type": "Assembly",
        "year": 2026,
        "seats": 126,
        "schedule": "April 2026",
        "status": "upcoming",
    },
]
