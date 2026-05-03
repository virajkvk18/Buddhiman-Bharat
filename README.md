---
title: Buddhiman Bharat
emoji: 🗳️
colorFrom: orange
colorTo: green
sdk: streamlit
sdk_version: 1.35.0
app_file: app.py
pinned: false
license: mit
---

# 🗳️ Buddhiman Bharat — भारत का बुद्धिमान चुनाव सहायक

> **India's Smartest AI-Powered Election Intelligence Platform**

[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?logo=streamlit)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Powered%20by-Gemini%201.5%20Flash-4285F4?logo=google)](https://ai.google.dev)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-45%20passing-brightgreen)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📌 Chosen Vertical

**Civic Technology / Democratic Participation Assistant**

Buddhiman Bharat is an AI-powered election intelligence platform for Indian democracy. It empowers every Indian voter with real-time election data, streaming AI-driven Q&A, voter guides, manifesto comparisons, fake news detection, and civic education — all in 16 Indian languages.

---

## 🚀 Architecture

```
buddhiman-bharat/
├── app.py                         # Main Streamlit entry point
├── config/
│   └── settings.py                # Centralised config, all API keys, constants
├── services/
│   ├── gemini_service.py          # Gemini 1.5 Flash — streaming AI, quick answers
│   ├── election_api.py            # ECI data + local election JSON (cached)
│   ├── maps_service.py            # Google Maps Embed + Geocoding + Static Maps
│   ├── google_sheets.py           # Google Sheets read/write + Forms integration
│   └── fact_check.py              # Google Fact Check Tools API + local myth DB
├── components/
│   ├── theme.py                   # WCAG 2.1 AA CSS design system
│   ├── ai_assistant.py            # Streaming chatbot: typing indicator, export
│   ├── voter_guide.py             # Checklist, rights, EVM, Google Maps embed
│   ├── results_dashboard.py       # Live results with Plotly charts
│   ├── manifesto_analyzer.py      # Party manifesto AI comparison
│   ├── fake_news_checker.py       # Fact-check UI + myth-busters
│   ├── voter_feedback.py          # Google Sheets feedback + live notifications
│   └── language_selector.py       # 16-language i18n with auto-detection
├── views/
│   └── dashboard.py               # Dashboard with metrics, map, notifications
├── utils/
│   ├── cache.py                   # TTL in-memory cache with @cached decorator
│   ├── location_utils.py          # PIN→State, state name parser, XSS sanitiser
│   └── validators.py              # Input validation, rate limiting, safe URLs
├── data/
│   ├── elections_2024_2026.json   # All 2024 election results + 2026 upcoming
│   └── voter_rights.json          # Rights, documents, checklist, MCC points
└── tests/                         # 45 tests across 8 test files
    ├── conftest.py                 # Shared fixtures
    ├── test_validators.py
    ├── test_location_utils.py
    ├── test_election_api.py
    ├── test_fact_check.py
    ├── test_gemini_service.py
    ├── test_cache.py
    ├── test_maps_service.py
    ├── test_google_sheets.py
    └── test_rate_limiting.py
```

---

## 🧠 Approach & Logic

### Decision Flow
1. User enters PIN / state → `location_utils` maps to state code
2. `election_api` loads election context (cached 5 min via `utils/cache`)
3. User asks AI → `validators` checks for injection, rate limit enforced
4. `gemini_service` checks quick-answer DB first → no API call if matched
5. If Gemini call needed → **streaming** response with typing indicator
6. Any election claim in query → auto fact-check via Google Fact Check API
7. Voter feedback → writes to **Google Sheets** via Apps Script webhook
8. Booth locator → **Google Maps Embed API** iframe in Voter Guide tab

### Google Services Used
| Service | Integration |
|---|---|
| **Gemini 1.5 Flash** | Streaming AI chatbot with context memory |
| **Google Maps Embed API** | Polling booth / DEO office map in Voter Guide |
| **Google Maps Geocoding API** | Address → lat/lng for booth search |
| **Google Maps Static Maps API** | Fallback static map images |
| **Google Fact Check Tools API** | Real-time claim verification |
| **Google Sheets API** | Read live election updates from admin sheet |
| **Google Apps Script** | Write voter feedback to Sheets (webhook) |
| **Google Forms** | Fallback feedback collection |

---

## ⚙️ Setup

```bash
git clone https://github.com/YOUR_USERNAME/buddhiman-bharat
cd buddhiman-bharat
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Add your API keys
streamlit run app.py
```

### Required / Optional Keys (.env)

| Variable | Required | Purpose |
|---|---|---|
| `GOOGLE_API_KEY` | ✅ Yes | Gemini AI (free at aistudio.google.com) |
| `GOOGLE_MAPS_KEY` | Optional | Google Maps embed, geocoding, static maps |
| `FACT_CHECK_API_KEY` | Optional | Google Fact Check Tools API |
| `GOOGLE_SHEETS_KEY` | Optional | Read live updates from Google Sheet |
| `GOOGLE_SHEETS_WEBHOOK` | Optional | Write feedback to Google Sheets |
| `GOOGLE_FORM_ID` | Optional | Fallback feedback Google Form |

---

## 🧪 Tests

```bash
pytest tests/ -v --tb=short
```

**45 tests** across: validators, location utils, election API, fact check, Gemini service, cache, Maps service, Google Sheets, rate limiting.

---

## 🔒 Security

- **Prompt injection detection** — 8 regex patterns blocking jailbreak attempts
- **Rate limiting** — 20 calls/60s per session, enforced in `validators.py`
- **XSS sanitisation** — all user inputs sanitised before rendering
- **URL safety check** — `is_safe_url()` validates external links against allowlist
- **HTML stripping** — all inputs stripped of HTML before processing
- **Control character removal** — null bytes and non-printable chars removed

---

## ♿ Accessibility (WCAG 2.1 AA)

- Skip navigation link
- `role` and `aria-label` on all interactive regions
- `aria-live` on status updates
- `aria-hidden` on decorative elements
- High-contrast focus indicators
- Reduced-motion support via `@media (prefers-reduced-motion)`
- High-contrast mode support

---

## 📋 Assumptions

- Users have basic smartphone/web access
- ECI data fetched from publicly available portals
- AI responses capped at 180 words for accessibility
- PIN codes follow India Post 6-digit format
- All 28 states + 8 UTs supported

---

## 🌐 Live Demo

**Hugging Face Spaces:** `https://huggingface.co/spaces/YOUR_USERNAME/buddhiman-bharat`

---

*Built with ❤️ for Indian democracy · भारतीय लोकतंत्र के लिए · ECI Helpline: 1950*
