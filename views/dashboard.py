"""
views/dashboard.py — Main dashboard view for Buddhiman Bharat
"""

import streamlit as st
from datetime import datetime
from config.settings import UPCOMING_ELECTIONS, PARTIES, INDIA
from components.language_selector import T
from services.election_api import get_national_result_summary


def render_dashboard() -> None:
    """Render the main dashboard overview."""
    election_data = st.session_state.get("election_data", {})
    state_name = election_data.get("state", "India") if election_data else "India"
    state_code = st.session_state.get("state_code", "")

    st.markdown(f"## 🇮🇳 {T('Dashboard')} — {state_name}")

    # Top metric row
    _render_hero_metrics(election_data)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # Two-column layout
    col_left, col_right = st.columns([1.6, 1])

    with col_left:
        _render_upcoming_elections(state_code)

    with col_right:
        _render_quick_actions()

    st.markdown("---")
    _render_lok_sabha_snapshot()

    st.markdown("---")
    _render_sveep_banner()

    # Live updates from Google Sheets (silent if not configured)
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    try:
        from components.voter_feedback import render_election_notifications
        render_election_notifications()
    except Exception:
        pass

    # Feedback form
    st.markdown("---")
    try:
        from components.voter_feedback import render_feedback_form
        render_feedback_form()
    except Exception:
        pass


def _render_hero_metrics(election_data: dict) -> None:
    """Render top-row metric cards."""
    national = get_national_result_summary()
    upcoming = election_data.get("upcoming") if election_data else None
    days_to_election = None

    if upcoming:
        # Rough estimate
        days_to_election = "2025–26"

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            """<div class="bb-card bb-metric-saffron">
            <div class="bb-card-title">🇮🇳 General Election</div>
            <div class="bb-card-value">18th</div>
            <div class="bb-card-sub">Lok Sabha · Jun 2024</div>
            </div>""",
            unsafe_allow_html=True,
        )

    with c2:
        turnout = national.get("turnout_percent", 65.79)
        st.markdown(
            f"""<div class="bb-card bb-metric-green">
            <div class="bb-card-title">📊 2024 Turnout</div>
            <div class="bb-card-value">{turnout:.1f}%</div>
            <div class="bb-card-sub">64.2 crore votes cast</div>
            </div>""",
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """<div class="bb-card">
            <div class="bb-card-title">🗳️ Registered Voters</div>
            <div class="bb-card-value">97Cr+</div>
            <div class="bb-card-sub">Largest democracy on Earth</div>
            </div>""",
            unsafe_allow_html=True,
        )

    with c4:
        upcoming_count = len(UPCOMING_ELECTIONS)
        st.markdown(
            f"""<div class="bb-card bb-metric-saffron">
            <div class="bb-card-title">📅 Upcoming Elections</div>
            <div class="bb-card-value">{upcoming_count}</div>
            <div class="bb-card-sub">State elections 2025–26</div>
            </div>""",
            unsafe_allow_html=True,
        )


def _render_upcoming_elections(current_state_code: str) -> None:
    """Render upcoming election timeline."""
    st.markdown("### 📅 Upcoming State Elections")

    for election in UPCOMING_ELECTIONS:
        is_current = election["state_code"] == current_state_code
        border = "border-left: 3px solid #FF6B1A;" if is_current else ""
        badge = " 📍 <em style='color:#FF6B1A;font-size:0.75rem;'>Your State</em>" if is_current else ""

        st.markdown(
            f"""<div class="bb-card" style="padding:14px;{border}margin-bottom:10px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <div>
                <div style="font-weight:800;color:#E8EAF0;font-size:0.95rem;">{election['state']}{badge}</div>
                <div style="color:#9BA3BC;font-size:0.8rem;margin-top:2px;">
                  {election['type']} · {election['seats']} seats · {election['schedule']}
                </div>
              </div>
              <div style="text-align:right;">
                <div style="background:#FF6B1A;color:white;padding:4px 10px;border-radius:12px;font-size:0.72rem;font-weight:700;">
                  {election['status'].upper()}
                </div>
              </div>
            </div></div>""",
            unsafe_allow_html=True,
        )


def _render_quick_actions() -> None:
    """Render quick action card panel."""
    st.markdown("### ⚡ Quick Actions")

    actions = [
        ("🗺️", "Find Your Booth", INDIA["VOTER_PORTAL"], "Locate your polling station"),
        ("📝", "Register to Vote", INDIA["NVSP_URL"], "New voter registration"),
        ("📱", "Download EPIC", INDIA["NVSP_URL"], "Get your digital Voter ID"),
        ("🚨", "Report Violation", "https://cvigil.eci.gov.in", "cVIGIL — 100 min action"),
        ("📞", "ECI Helpline", f"tel:{INDIA['VOTER_HELPLINE']}", "Call 1950 (toll-free)"),
        ("📊", "Check Roll", INDIA["VOTER_PORTAL"], "Verify your enrollment"),
    ]

    for icon, label, url, desc in actions:
        st.markdown(
            f"""<a href="{url}" target="_blank" style="text-decoration:none;">
            <div class="bb-card" style="padding:12px;cursor:pointer;display:flex;align-items:center;gap:12px;margin-bottom:8px;">
              <span style="font-size:1.4rem;">{icon}</span>
              <div>
                <div style="font-weight:700;color:#E8EAF0;font-size:0.88rem;">{label}</div>
                <div style="font-size:0.75rem;color:#9BA3BC;">{desc}</div>
              </div>
            </div></a>""",
            unsafe_allow_html=True,
        )


def _render_lok_sabha_snapshot() -> None:
    """Render 2024 Lok Sabha result snapshot."""
    st.markdown("### 🏛️ 2024 Lok Sabha — Final Results Snapshot")
    national = get_national_result_summary()
    results = national.get("results", {})

    if not results:
        return

    party_colors = {
        "BJP": "#FF6B00", "INC": "#00A3E0", "SP": "#FF0000",
        "TMC": "#29ABE2", "DMK": "#CC0000", "TDP": "#FFFF00",
        "JDU": "#00A86B", "Others": "#5C6480",
    }

    cols = st.columns(len(results))
    for i, (party, res) in enumerate(sorted(results.items(), key=lambda x: -x[1]["seats"])):
        with cols[i]:
            color = party_colors.get(party, "#888")
            party_info = PARTIES.get(party, {})
            seats = res["seats"]
            pct = seats / 543 * 100
            bar_h = max(20, int(pct * 1.8))

            st.markdown(
                f"""<div style="text-align:center;padding:8px;">
                <div style="font-size:1.2rem;">{party_info.get('symbol','')}</div>
                <div style="height:{bar_h}px;width:24px;background:{color};margin:6px auto;border-radius:4px;"></div>
                <div style="font-weight:800;color:{color};font-size:0.9rem;">{seats}</div>
                <div style="font-size:0.7rem;color:#9BA3BC;">{party}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="bb-alert bb-alert-info" style="margin-top:12px;">'
        '🏆 <strong>NDA wins majority (293 seats)</strong> · PM Narendra Modi sworn in for 3rd term on June 9, 2024'
        '</div>',
        unsafe_allow_html=True,
    )


def _render_sveep_banner() -> None:
    """Render SVEEP voter awareness banner."""
    st.markdown(
        f"""<div style="background:linear-gradient(135deg,rgba(255,107,26,0.15),rgba(19,136,8,0.15));
        border:1px solid rgba(255,107,26,0.3);border-radius:12px;padding:20px;text-align:center;margin-top:8px;">
        <div style="font-size:2rem;margin-bottom:8px;">🗳️</div>
        <div style="font-size:1.1rem;font-weight:800;color:#E8EAF0;margin-bottom:6px;">
          Every Vote Counts — हर वोट कीमती है
        </div>
        <div style="color:#9BA3BC;font-size:0.88rem;margin-bottom:14px;">
          India's democracy is built on your participation. Register, inform yourself, and vote!
        </div>
        <a href="{INDIA['SVEEP_URL']}" target="_blank" style="text-decoration:none;">
          <div style="display:inline-block;background:#FF6B1A;color:white;padding:8px 20px;
          border-radius:8px;font-weight:700;font-size:0.88rem;">
            Learn More at SVEEP →
          </div>
        </a>
        </div>""",
        unsafe_allow_html=True,
    )
