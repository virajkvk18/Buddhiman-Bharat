"""
components/language_selector.py — 16-language i18n for Buddhiman Bharat
"""

import streamlit as st
from config.settings import LANGUAGES

# Translation dictionary
_TRANSLATIONS: dict[str, dict[str, str]] = {
    "hi": {
        "AI Voter Assistant": "AI मतदाता सहायक",
        "Voter Guide": "मतदाता गाइड",
        "Results": "परिणाम",
        "Candidates": "उम्मीदवार",
        "Trends": "रुझान",
        "Exit Polls": "एग्जिट पोल",
        "Fact Checker": "तथ्य जाँच",
        "EVM Guide": "EVM गाइड",
        "Dashboard": "डैशबोर्ड",
        "Notifications": "सूचनाएं",
        "Map": "मानचित्र",
        "Change": "बदलें",
        "Search": "खोजें",
        "queries left": "प्रश्न शेष",
        "Thinking…": "सोच रहा हूँ…",
        "Your India Election Dashboard": "आपका भारत चुनाव डैशबोर्ड",
        "Ask about voting, registration, booth…": "मतदान, पंजीकरण, बूथ के बारे में पूछें…",
        "Upcoming Elections": "आगामी चुनाव",
        "Recent Results": "हाल के परिणाम",
        "Voter Checklist": "मतदाता चेकलिस्ट",
        "ECI Helpline": "ECI हेल्पलाइन",
        "Share Experience": "अनुभव साझा करें",
        "Quick Access": "त्वरित पहुँच",
        "Enter PIN or state": "PIN या राज्य दर्ज करें",
        "Party Manifestos": "पार्टी घोषणापत्र",
        "Fake News Checker": "फर्जी खबर जाँचक",
    },
    "bn": {
        "AI Voter Assistant": "AI ভোটার সহকারী",
        "Voter Guide": "ভোটার গাইড",
        "Results": "ফলাফল",
        "Dashboard": "ড্যাশবোর্ড",
        "Candidates": "প্রার্থী",
        "Trends": "প্রবণতা",
        "Search": "অনুসন্ধান",
        "Change": "পরিবর্তন",
        "Thinking…": "ভাবছি…",
        "Fact Checker": "তথ্য যাচাই",
        "EVM Guide": "EVM গাইড",
        "Upcoming Elections": "আসন্ন নির্বাচন",
    },
    "te": {
        "AI Voter Assistant": "AI ఓటర్ సహాయకుడు",
        "Dashboard": "డాష్‌బోర్డ్",
        "Results": "ఫలితాలు",
        "Candidates": "అభ్యర్థులు",
        "Search": "వెతకండి",
        "Change": "మార్చు",
        "Thinking…": "ఆలోచిస్తున్నాను…",
        "Voter Guide": "ఓటరు గైడ్",
        "Fact Checker": "వాస్తవ తనిఖీ",
    },
    "ta": {
        "AI Voter Assistant": "AI வாக்காளர் உதவியாளர்",
        "Dashboard": "டாஷ்போர்டு",
        "Results": "முடிவுகள்",
        "Candidates": "வேட்பாளர்கள்",
        "Search": "தேடு",
        "Change": "மாற்று",
        "Thinking…": "யோசிக்கிறேன்…",
        "Voter Guide": "வாக்காளர் வழிகாட்டி",
    },
    "mr": {
        "AI Voter Assistant": "AI मतदार सहाय्यक",
        "Dashboard": "डॅशबोर्ड",
        "Results": "निकाल",
        "Candidates": "उमेदवार",
        "Search": "शोधा",
        "Change": "बदला",
        "Thinking…": "विचार करतोय…",
        "Voter Guide": "मतदार मार्गदर्शिका",
    },
    "gu": {
        "AI Voter Assistant": "AI મતદાર સહાયક",
        "Dashboard": "ડૅશબોર્ડ",
        "Results": "પરિણામો",
        "Search": "શોધો",
        "Change": "બદલો",
        "Thinking…": "વિચારી રહ્યો છું…",
    },
    "kn": {
        "AI Voter Assistant": "AI ಮತದಾರ ಸಹಾಯಕ",
        "Dashboard": "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "Results": "ಫಲಿತಾಂಶ",
        "Search": "ಹುಡುಕು",
        "Change": "ಬದಲಿಸು",
        "Thinking…": "ಯೋಚಿಸುತ್ತಿದ್ದೇನೆ…",
    },
    "ml": {
        "AI Voter Assistant": "AI വോട്ടർ അസിസ്റ്റന്റ്",
        "Dashboard": "ഡാഷ്‌ബോർഡ്",
        "Results": "ഫലങ്ങൾ",
        "Search": "തിരയുക",
        "Change": "മാറ്റുക",
        "Thinking…": "ചിന്തിക്കുന്നു…",
    },
    "pa": {
        "AI Voter Assistant": "AI ਵੋਟਰ ਸਹਾਇਕ",
        "Dashboard": "ਡੈਸ਼ਬੋਰਡ",
        "Results": "ਨਤੀਜੇ",
        "Search": "ਖੋਜੋ",
        "Change": "ਬਦਲੋ",
        "Thinking…": "ਸੋਚ ਰਿਹਾ ਹਾਂ…",
    },
}


def T(key: str) -> str:
    """Translate key to current session language. Falls back to English."""
    lang = st.session_state.get("language", "en")
    if lang == "en":
        return key
    return _TRANSLATIONS.get(lang, {}).get(key, key)


def render_language_selector() -> None:
    """Render compact language selector dropdown."""
    lang_options = list(LANGUAGES.keys())
    lang_labels = [f"{LANGUAGES[l]}" for l in lang_options]
    current = st.session_state.get("language", "en")
    current_idx = lang_options.index(current) if current in lang_options else 0

    selected_label = st.selectbox(
        "🌐 Language",
        options=lang_labels,
        index=current_idx,
        key="lang_selector",
        label_visibility="collapsed",
        help="Select your preferred language / अपनी भाषा चुनें",
    )
    selected_code = lang_options[lang_labels.index(selected_label)]
    if selected_code != st.session_state.get("language", "en"):
        st.session_state["language"] = selected_code
        st.rerun()
