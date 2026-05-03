"""
Buddhiman Bharat (बुद्धिमान भारत)
====================================
India's Smartest AI-Powered Election Intelligence Platform

Entry point — all heavy render logic lives in views/ and components/.
"""

import streamlit as st
import logging
import sys
from dotenv import load_dotenv

load_dotenv()

# ── Logging Configuration ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
# Suppress noisy third-party loggers
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("google").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# ── Config (must be first Streamlit call) ─────────────────────────────────────
st.set_page_config(
    page_title="Buddhiman Bharat | भारत का चुनाव सहायक",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": "https://eci.gov.in",
        "Report a bug": None,
        "About": "Buddhiman Bharat — AI Election Intelligence for Every Indian Voter",
    },
)

from config.settings import GOOGLE_API_KEY, INDIA
from components.theme import DARK_THEME_CSS, ACCESSIBILITY_CSS, SKIP_LINK_HTML
from components.language_selector import render_language_selector, T
from components.ai_assistant import render_ai_assistant
from components.voter_guide import render_voter_guide
from components.results_dashboard import render_results_dashboard
from components.manifesto_analyzer import render_manifesto_analyzer
from components.fake_news_checker import render_fake_news_checker
from views.dashboard import render_dashboard
from services.election_api import get_election_data_for_location
from utils.location_utils import parse_location, sanitize_text
from utils.validators import validate_location_input

logger = logging.getLogger(__name__)

# ── Session State Defaults ────────────────────────────────────────────────────

def init_session() -> None:
    defaults = {
        "location": "",
        "state_code": "",
        "election_data": None,
        "language": "en",
        "ai_messages": [],
        "ai_query_count": 0,
        "checklist_done": set(),
        "saved_pins": [
            "110001 — New Delhi", "700001 — West Bengal",
            "400001 — Mumbai", "600001 — Chennai",
        ],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def process_location(location: str) -> bool:
    """Parse location and load election data into session."""
    if not validate_location_input(location):
        return False
    parsed = parse_location(location)
    election_data = get_election_data_for_location(location)
    st.session_state.update({
        "location": location,
        "state_code": parsed.get("state_code") or "",
        "election_data": election_data,
    })
    return True


# ── UI Components ─────────────────────────────────────────────────────────────

def render_topnav() -> None:
    """Render sticky top navigation bar."""
    state_name = ""
    if st.session_state.get("election_data"):
        state_name = st.session_state["election_data"].get("state", "")

    st.markdown(
        f"""
        <nav class="bb-topnav" role="navigation" aria-label="Buddhiman Bharat main navigation">
          <div class="bb-logo" aria-label="Buddhiman Bharat logo">
            <div class="bb-logo-icon" aria-hidden="true">BB</div>
            <div>
              <div class="bb-logo-title">Buddhiman Bharat</div>
              <div class="bb-logo-sub">बुद्धिमान भारत · AI Election Intelligence</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:16px;">
            {"<div style='font-size:0.8rem;color:#9BA3BC;'>📍 " + sanitize_text(state_name) + "</div>" if state_name else ""}
            <div class="bb-live-badge" role="status" aria-live="polite">
              <div class="bb-live-dot" aria-hidden="true"></div>
              <span>INDIA ELECTIONS 2025–26</span>
            </div>
          </div>
        </nav>
        <div class="bb-tricolour" aria-hidden="true"></div>
        """,
        unsafe_allow_html=True,
    )


def render_location_bar() -> None:
    """Render location info bar with language selector and change button."""
    election_data = st.session_state.get("election_data", {})
    jurisdiction = election_data.get("jurisdiction", st.session_state.get("location", "")) if election_data else ""
    location = st.session_state.get("location", "")

    col_info, col_lang, col_change = st.columns([3, 1.2, 0.8])

    with col_info:
        st.markdown(
            f"""<div role="region" aria-label="Current location: {sanitize_text(jurisdiction)}"
              style="background:#181B26;border:1px solid rgba(255,255,255,0.08);
              border-radius:8px;padding:10px 14px;display:flex;align-items:center;gap:10px;">
              <span aria-hidden="true" style="font-size:1rem;">📍</span>
              <span style="font-size:0.9rem;font-weight:700;color:#E8EAF0;">{sanitize_text(jurisdiction)}</span>
              <span style="font-size:0.75rem;color:#5C6480;">· {sanitize_text(location)}</span>
            </div>""",
            unsafe_allow_html=True,
        )

    with col_lang:
        render_language_selector()

    with col_change:
        if st.button(f"↩️ {T('Change')}", use_container_width=True, help="Change your location"):
            st.session_state.update({
                "location": "",
                "election_data": None,
                "state_code": "",
            })
            st.rerun()


def render_home_screen() -> None:
    """Render PIN/state entry screen (pre-location)."""
    st.markdown(
        """
        <main id="main-content" role="main">
          <div style="max-width:580px;margin:3rem auto 0;text-align:center;padding:0 1.5rem;">
            <div style="font-size:3.5rem;margin-bottom:16px;" aria-hidden="true">🗳️</div>
            <h1 style="font-size:2rem;font-weight:800;color:#E8EAF0;
              font-family:'DM Sans',sans-serif;margin-bottom:8px;line-height:1.2;">
              Buddhiman Bharat
            </h1>
            <p style="font-size:1.1rem;color:#FF6B1A;font-weight:700;margin-bottom:8px;">
              बुद्धिमान भारत
            </p>
            <p style="color:#9BA3BC;font-size:0.95rem;margin-bottom:32px;line-height:1.7;">
              India's smartest AI election assistant. Get live results, voter guides,
              manifesto comparisons, fact-checking & AI support — all in your language.
            </p>
          </div>
        </main>
        """,
        unsafe_allow_html=True,
    )

    # Search bar
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        loc = st.text_input(
            "PIN or State",
            label_visibility="collapsed",
            placeholder="Enter 6-digit PIN or state name (e.g. Bihar, 400001)",
            key="home_location",
            help="Enter your Indian PIN code or state name to load election data",
        )
        go_clicked = st.button("🔍 Explore Elections", type="primary", use_container_width=True)

        if (go_clicked or loc) and loc:
            if validate_location_input(loc):
                if process_location(loc):
                    st.rerun()
                else:
                    st.error("Could not load election data. Please try another location.")
            else:
                st.error("Please enter a valid 6-digit PIN code or Indian state name.")

        st.markdown(
            '<p style="text-align:center;font-size:0.75rem;color:#5C6480;margin:16px 0 8px;'
            'font-weight:600;text-transform:uppercase;letter-spacing:0.08em;">Quick Access</p>',
            unsafe_allow_html=True,
        )
        pin_cols = st.columns(2)
        for i, pin in enumerate(st.session_state.get("saved_pins", [])):
            with pin_cols[i % 2]:
                if st.button(pin, key=f"quick_{i}", use_container_width=True):
                    raw_pin = pin.split(" — ")[0].strip()
                    if process_location(raw_pin):
                        st.rerun()

    # ── Home-screen Quick Chat ────────────────────────────────────────────────
    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """<div style="max-width:580px;margin:0 auto;">
        <p style="text-align:center;font-size:0.82rem;color:#5C6480;margin-bottom:8px;font-weight:600;">
        ⚡ OR start chatting directly without entering a location
        </p></div>""",
        unsafe_allow_html=True,
    )
    _, mid2, _ = st.columns([1, 2, 1])
    with mid2:
        quick_q = st.text_input(
            "Quick chat",
            label_visibility="collapsed",
            placeholder="💬 Ask the AI: 'How do I find my booth?'",
            key="home_quick_chat",
        )
        if quick_q and quick_q.strip():
            # Load generic election data and go to chat
            process_location("India")
            st.session_state.setdefault("ai_messages", [])
            from services.gemini_service import GREETING_MESSAGE
            if not st.session_state["ai_messages"]:
                from datetime import datetime as _dt
                st.session_state["ai_messages"] = [
                    {"role": "assistant", "content": GREETING_MESSAGE, "ts": _dt.now().strftime("%I:%M %p")}
                ]
            st.rerun()

    # Feature highlights
    st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center;font-size:0.88rem;color:#5C6480;margin-bottom:20px;">✨ What Buddhiman Bharat offers</p>',
        unsafe_allow_html=True,
    )

    features = [
        ("🤖", "Gemini AI Assistant", "Ask any election question in your language — Hindi, Bengali, Tamil & 13 more."),
        ("📊", "Live Results", "2024 Lok Sabha & Assembly results with interactive Plotly charts."),
        ("📋", "Party Manifestos", "AI-powered neutral comparison of party promises."),
        ("🔍", "Fake News Checker", "Instantly verify election rumours with Google Fact Check API."),
        ("✅", "Voter Checklist", "Step-by-step guide to prepare for Election Day."),
        ("🗳️", "EVM Guide", "Understand EVMs, VVPAT and your voting rights."),
    ]

    feat_cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with feat_cols[i % 3]:
            st.markdown(
                f"""<div class="bb-card" style="text-align:center;padding:20px;">
                <div style="font-size:2rem;margin-bottom:10px;">{icon}</div>
                <div style="font-weight:700;color:#E8EAF0;margin-bottom:6px;">{title}</div>
                <div style="font-size:0.82rem;color:#9BA3BC;line-height:1.5;">{desc}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    # Footer
    st.markdown(
        f"""<div class="bb-footer">
        🗳️ <strong>Buddhiman Bharat</strong> — Independent, Non-partisan · Built for Indian Democracy<br>
        <span style="color:#5C6480;">Data sourced from ECI · ECI Helpline: {INDIA['VOTER_HELPLINE']}</span>
        </div>""",
        unsafe_allow_html=True,
    )


# ── Main App ──────────────────────────────────────────────────────────────────

def main() -> None:
    init_session()

    # Inject styles
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
    st.markdown(ACCESSIBILITY_CSS, unsafe_allow_html=True)
    st.markdown(SKIP_LINK_HTML, unsafe_allow_html=True)

    # Security headers + lang attribute (injected via meta tags)
    st.markdown(
        """
        <meta http-equiv="X-Content-Type-Options" content="nosniff">
        <meta http-equiv="X-Frame-Options" content="SAMEORIGIN">
        <meta http-equiv="Content-Security-Policy"
          content="default-src 'self' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:;
                   style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
                   font-src https://fonts.gstatic.com; img-src 'self' data: https:;
                   frame-src https://maps.google.com https://www.google.com;">
        <meta name="referrer" content="strict-origin-when-cross-origin">
        <script>document.documentElement.setAttribute('lang',
          (window.__streamlit_session_state && window.__streamlit_session_state.language) || 'en');
        </script>
        """,
        unsafe_allow_html=True,
    )

    render_topnav()

    # Show home screen if no location set
    if not st.session_state.get("election_data"):
        render_home_screen()
        return

    # Location bar
    render_location_bar()
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # Pull session data
    election_data = st.session_state["election_data"]
    state_code = st.session_state.get("state_code", "")
    state_name = election_data.get("state", "India")

    # Main tabs — AI chatbot is tab 0 (default)
    tabs = st.tabs([
        f"🤖 {T('AI Voter Assistant')}",
        f"🏠 {T('Dashboard')}",
        f"📊 {T('Results')}",
        f"📋 {T('Voter Guide')}",
        f"📜 Manifestos",
        f"🔍 Fact Check",
    ])

    with tabs[0]:
        render_ai_assistant(election_data)

    with tabs[1]:
        render_dashboard()

    with tabs[2]:
        render_results_dashboard(state_code=state_code, state_name=state_name)

    with tabs[3]:
        render_voter_guide()

    with tabs[4]:
        render_manifesto_analyzer()

    with tabs[5]:
        render_fake_news_checker()

    # Footer
    st.markdown(
        f"""<div class="bb-footer">
        🗳️ Buddhiman Bharat — Independent & Non-partisan ·
        ECI Helpline: <strong>{INDIA['VOTER_HELPLINE']}</strong> ·
        <a href="{INDIA['ECI_WEBSITE']}" target="_blank" style="color:#FF6B1A;">eci.gov.in</a>
        </div>""",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
