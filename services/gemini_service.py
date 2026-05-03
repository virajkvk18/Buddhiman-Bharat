"""
services/gemini_service.py — Gemini AI integration with streaming & context memory
"""

import logging
import re
from typing import Generator, Optional
from config.settings import GOOGLE_API_KEY, GEMINI_MODEL, GEMINI_MAX_TOKENS, INDIA

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Buddhiman Bharat (बुद्धिमान भारत), India's most trusted AI election assistant — friendly, clear, and always non-partisan.

You help Indian voters with:
- Voter registration, EPIC card, booth location, name in electoral roll
- Candidate profiles and party manifestos (factual only)
- Election schedules, phases, dates, and ECI announcements
- Constitutional rights of voters, Model Code of Conduct
- How to use EVM and VVPAT machines
- Reporting violations via cVIGIL App or ECI Helpline 1950
- Fake news / misinformation around elections

STRICT RULES:
1. ALWAYS be factual, neutral, non-partisan. Never favour any party or candidate.
2. If asked for party preference, election predictions, or opinions — politely decline and give facts instead.
3. Respond in the EXACT SAME LANGUAGE the user writes in (Hindi, Bengali, Tamil, etc.)
4. Keep responses concise (under 180 words), use simple language accessible to all Indians.
5. Always include ECI Helpline 1950 for urgent voter issues.
6. For unverified claims say: "Please verify at eci.gov.in or call 1950."
7. For off-topic questions, gently redirect to election topics.
8. Format responses with bullet points or numbered lists when listing steps.
9. Use relevant emojis sparingly to make responses friendly.

Current context: {context}
"""

GREETING_MESSAGE = """🙏 **Namaste! I'm Buddhiman Bharat** — your AI election guide.

I can help you with:
• 🗳️ Voter registration & EPIC card
• 📍 Finding your polling booth
• 📋 Election dates & schedules
• ⚖️ Your voting rights
• 🔍 Checking election facts
• 🤖 EVM & VVPAT guide

**Ask me anything in your language** — हिंदी, বাংলা, தமிழ், తెలుగు, or English!

*ECI Helpline: **1950** (toll-free)*"""


def _build_context(election_data, state_code: str, language: str) -> str:
    if not election_data:
        return f"General Indian election queries. User language: {language}"
    return (
        f"Election: {election_data.get('election_name', 'Indian Elections')} | "
        f"State: {election_data.get('state', 'India')} | "
        f"State Code: {state_code} | "
        f"User language: {language}"
    )


def call_gemini(
    question: str,
    history: list,
    election_data=None,
    state_code: str = "",
    language: str = "en",
) -> str:
    """Call Gemini and return full text response."""
    if not GOOGLE_API_KEY:
        return (
            f"⚠️ AI not configured. Add `GOOGLE_API_KEY` to your `.env` file.\n"
            f"Get a free key at [aistudio.google.com](https://aistudio.google.com)\n\n"
            f"ECI Helpline: **{INDIA['VOTER_HELPLINE']}**"
        )

    try:
        import google.generativeai as genai

        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(
            GEMINI_MODEL,
            generation_config={
                "max_output_tokens": GEMINI_MAX_TOKENS,
                "temperature": 0.35,
                "top_p": 0.85,
                "top_k": 40,
            },
            safety_settings=[
                {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_LOW_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT",  "threshold": "BLOCK_LOW_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HARASSMENT",         "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",  "threshold": "BLOCK_LOW_AND_ABOVE"},
            ],
        )

        ctx = _build_context(election_data, state_code, language)
        system = SYSTEM_PROMPT.format(context=ctx)

        gemini_history = []
        for msg in history[-20:]:
            if msg["role"] in ("user", "assistant") and msg.get("content", "").strip():
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg["content"]]})

        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(f"{system}\n\nVoter question: {question}")
        return response.text or "I couldn't generate a response. Please try again."

    except ImportError:
        return "⚠️ AI package missing. Run: `pip install google-generativeai`"
    except Exception as exc:
        logger.error("Gemini API error: %s", exc)
        err = str(exc)
        if "API_KEY_INVALID" in err or "api key" in err.lower():
            return "⚠️ Invalid Gemini API key. Check your `GOOGLE_API_KEY`."
        if "quota" in err.lower() or "429" in err:
            return f"⚠️ Quota exceeded. Try again shortly or call **{INDIA['VOTER_HELPLINE']}**."
        return f"⚠️ Temporary AI error. ECI Helpline: **{INDIA['VOTER_HELPLINE']}**"


def call_gemini_streaming(
    question: str,
    history: list,
    election_data=None,
    state_code: str = "",
    language: str = "en",
):
    """Call Gemini with streaming — yields text chunks as a generator."""
    if not GOOGLE_API_KEY:
        yield f"⚠️ AI not configured. Add `GOOGLE_API_KEY` to `.env`.\n\nECI Helpline: **{INDIA['VOTER_HELPLINE']}**"
        return

    try:
        import google.generativeai as genai

        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(
            GEMINI_MODEL,
            generation_config={"max_output_tokens": GEMINI_MAX_TOKENS, "temperature": 0.35, "top_p": 0.85},
            safety_settings=[
                {"category": "HARM_CATEGORY_HATE_SPEECH",      "threshold": "BLOCK_LOW_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
            ],
        )

        ctx = _build_context(election_data, state_code, language)
        system = SYSTEM_PROMPT.format(context=ctx)

        gemini_history = []
        for msg in history[-20:]:
            if msg["role"] in ("user", "assistant") and msg.get("content", "").strip():
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg["content"]]})

        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(f"{system}\n\nVoter question: {question}", stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    except Exception as exc:
        logger.error("Gemini streaming error: %s", exc)
        err = str(exc)
        if "API_KEY_INVALID" in err or "api key" in err.lower():
            yield "⚠️ Invalid API key. Check your `GOOGLE_API_KEY`."
        elif "quota" in err.lower() or "429" in err:
            yield f"⚠️ Quota exceeded. Try again shortly or call **{INDIA['VOTER_HELPLINE']}**."
        else:
            yield f"⚠️ AI error. ECI Helpline: **{INDIA['VOTER_HELPLINE']}**"


def detect_language_from_text(text: str) -> str:
    """Detect probable language from Unicode character ranges."""
    if not text:
        return "en"
    checks = [
        (r"[\u0900-\u097F]", "hi"),
        (r"[\u0980-\u09FF]", "bn"),
        (r"[\u0C00-\u0C7F]", "te"),
        (r"[\u0B80-\u0BFF]", "ta"),
        (r"[\u0A80-\u0AFF]", "gu"),
        (r"[\u0C80-\u0CFF]", "kn"),
        (r"[\u0D00-\u0D7F]", "ml"),
        (r"[\u0A00-\u0A7F]", "pa"),
        (r"[\u0600-\u06FF]", "ur"),
    ]
    for pattern, lang in checks:
        if re.search(pattern, text):
            return lang
    return "en"


def get_quick_answers(query: str):
    """Return instant answers for very common voter queries — no API call needed."""
    q = query.lower().strip()

    quick = {
        ("voter id", "epic card", "voter card", "download voter"):
            "📋 **Download your Voter ID (EPIC) free:**\n"
            "1. Visit **nvsp.in** → 'Download e-EPIC'\n"
            "2. Or use the **Voter Helpline App** (Android/iOS)\n"
            "3. Or visit **voterportal.eci.gov.in**\n\n"
            "You need your EPIC number or registered mobile. Helpline: **1950**",

        ("polling booth", "voting booth", "where to vote", "my booth"):
            "📍 **Find your polling booth:**\n"
            "1. SMS `ECI <space> EPIC-number` to **1950**\n"
            "2. Visit **voterportal.eci.gov.in** → 'Know Your Polling Station'\n"
            "3. Use **Voter Helpline App** → 'Find Polling Station'\n\n"
            "Your booth is within 2km of your registered address.",

        ("nota", "none of the above"):
            "🗳️ **NOTA (None of the Above):**\n"
            "• Appears as the **last button** on every EVM\n"
            "• Introduced by Supreme Court order in 2013\n"
            "• NOTA votes are **counted but don't transfer** to any candidate\n"
            "• Even if NOTA gets most votes, the candidate with next-highest votes wins\n"
            "• It's your right to reject all candidates!",

        ("evm", "electronic voting machine", "evm hack", "evm tamper"):
            "🔒 **EVM Security Facts:**\n"
            "• **No internet, WiFi, or Bluetooth** — completely standalone\n"
            "• Cannot be remotely accessed after sealing\n"
            "• **VVPAT** prints a paper slip for 7 seconds — verify your vote\n"
            "• Supreme Court upheld EVM integrity multiple times\n\n"
            "Any concerns? Call ECI Helpline: **1950**",

        ("helpline", "complaint", "report violation", "cvigil"):
            "🚨 **Report Election Issues:**\n"
            "• 📞 **ECI Helpline: 1950** — toll-free, 24x7 during elections\n"
            "• 📱 **cVIGIL App** — geo-tagged reports, action in 100 min\n"
            "• 🌐 **eci.gov.in** → Grievances\n"
            "• 🏛️ Visit your District Election Officer",

        ("register", "new voter", "enroll", "form 6"):
            "📝 **Register as a New Voter:**\n"
            "1. Visit **voterportal.eci.gov.in** → 'New Registration' (Form 6)\n"
            "2. Or use **Voter Helpline App** → Register\n"
            "3. Or visit nearest **BLO** (Booth Level Officer)\n\n"
            "**Eligibility:** Indian citizen, 18+ years\n"
            "Documents: Aadhaar/Passport + address proof + photo",

        ("aadhaar", "aadhar compulsory", "aadhaar mandatory"):
            "⚠️ **Aadhaar is NOT mandatory to vote!**\n\n"
            "Any ONE of 12 valid documents is accepted:\n"
            "• Voter ID (EPIC), Aadhaar, Passport, Driving Licence, PAN Card\n"
            "• MNREGA Job Card, Bank passbook with photo + 6 more\n\n"
            "Minor spelling errors in your name don't disqualify you!",
    }

    for keywords, answer in quick.items():
        if any(kw in q for kw in keywords):
            return answer
    return None
