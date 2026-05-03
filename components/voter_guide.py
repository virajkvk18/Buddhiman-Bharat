"""
components/voter_guide.py — Voter guide, checklist, rights & EVM awareness
"""

import json
import os
import streamlit as st
from config.settings import INDIA
from components.language_selector import T

_RIGHTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "voter_rights.json")


def _load_rights() -> dict:
    try:
        with open(_RIGHTS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def render_voter_guide() -> None:
    """Render the full voter guide tab."""
    rights = _load_rights()

    tab_checklist, tab_rights, tab_docs, tab_evm, tab_mcc = st.tabs([
        "✅ Checklist", "⚖️ Your Rights", "📋 ID Documents", "🗳️ EVM Guide", "📜 MCC"
    ])

    with tab_checklist:
        _render_checklist(rights)

    with tab_rights:
        _render_rights(rights)

    with tab_docs:
        _render_documents(rights)

    with tab_evm:
        _render_evm_guide()

    with tab_mcc:
        _render_mcc(rights)


def _render_checklist(rights: dict) -> None:
    """Render interactive voter checklist with persistent state."""
    st.markdown("### ✅ Voter Checklist")
    st.markdown(
        "<p style='color:#9BA3BC;font-size:0.88rem;'>Complete all steps before Election Day</p>",
        unsafe_allow_html=True,
    )

    checklist = rights.get("voter_checklist", [])
    completed = st.session_state.setdefault("checklist_done", set())
    total = len(checklist)
    done_count = len(completed)
    pct = int(done_count / total * 100) if total else 0

    # Progress bar
    st.markdown(
        f"""<div style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
          <span style="font-weight:700;color:#E8EAF0;">Progress</span>
          <span style="color:#FF6B1A;font-weight:700;">{done_count}/{total} · {pct}%</span>
        </div>
        <div style="background:#1A1D2E;border-radius:8px;height:10px;overflow:hidden;">
          <div style="width:{pct}%;height:100%;
            background:linear-gradient(90deg,#FF6B1A,#138808);
            border-radius:8px;transition:width 0.4s;"></div>
        </div></div>""",
        unsafe_allow_html=True,
    )

    for item in checklist:
        step = item["step"]
        task = item["task"]
        url = item.get("url")
        key = f"check_{step}"
        is_done = step in completed

        col_check, col_text = st.columns([0.08, 0.92])
        with col_check:
            checked = st.checkbox("", value=is_done, key=key, label_visibility="collapsed")
            if checked:
                completed.add(step)
            elif step in completed:
                completed.discard(step)

        with col_text:
            text_style = "text-decoration:line-through;color:#5C6480;" if checked else "color:#E8EAF0;"
            link = f' <a href="{url}" target="_blank" style="color:#FF6B1A;font-size:0.75rem;">[Visit →]</a>' if url else ""
            st.markdown(
                f'<div style="{text_style}font-size:0.9rem;padding:6px 0;">'
                f'<strong>Step {step}:</strong> {task}{link}</div>',
                unsafe_allow_html=True,
            )

    if done_count == total:
        st.markdown(
            """<div class="bb-alert bb-alert-success" style="margin-top:12px;">
            🎉 <strong>You're fully prepared to vote!</strong>
            Share this app with 5 friends and help India vote smarter.
            </div>""",
            unsafe_allow_html=True,
        )

    # Helpful links
    st.markdown("---")
    st.markdown("#### 🔗 Quick Links")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.link_button("🗳️ Voter Portal", INDIA["VOTER_PORTAL"], use_container_width=True)
    with col2:
        st.link_button("📝 NVSP Registration", INDIA["NVSP_URL"], use_container_width=True)
    with col3:
        st.link_button("📞 ECI Website", INDIA["ECI_WEBSITE"], use_container_width=True)

    # Google Maps embed — nearest DEO office
    st.markdown("---")
    st.markdown("#### 🗺️ Find Your District Election Office")
    state_code = st.session_state.get("state_code", "DL")
    try:
        from services.maps_service import get_booth_iframe_html
        iframe = get_booth_iframe_html(state_code, height=280)
        st.markdown(iframe, unsafe_allow_html=True)
        st.markdown(
            f"<p style='font-size:0.75rem;color:#5C6480;margin-top:6px;'>"
            f"📍 Showing District Election Office for your region. "
            f"<a href='https://voterportal.eci.gov.in' target='_blank' style='color:#FF6B1A;'>"
            f"Find exact booth at voterportal.eci.gov.in →</a></p>",
            unsafe_allow_html=True,
        )
    except Exception:
        st.link_button("🗺️ Open Booth Map", INDIA["VOTER_PORTAL"], use_container_width=True)


def _render_rights(rights: dict) -> None:
    """Render voter rights section."""
    st.markdown("### ⚖️ Your Constitutional Rights as a Voter")
    for i, right in enumerate(rights.get("fundamental_rights", []), 1):
        st.markdown(
            f"""<div class="bb-card" style="padding:14px;margin-bottom:10px;">
            <div style="display:flex;gap:12px;align-items:flex-start;">
              <div class="bb-step-num">{i}</div>
              <div style="color:#E8EAF0;font-size:0.9rem;line-height:1.6;">{right}</div>
            </div></div>""",
            unsafe_allow_html=True,
        )
    st.markdown(
        f"""<div class="bb-alert bb-alert-info">
        📞 <strong>ECI Voter Helpline: {INDIA['VOTER_HELPLINE']}</strong> — toll-free, available 24x7 during elections.
        Report violations instantly via the <strong>cVIGIL App</strong>.
        </div>""",
        unsafe_allow_html=True,
    )


def _render_documents(rights: dict) -> None:
    """Render accepted ID documents grid."""
    st.markdown("### 📋 Accepted Voter Identity Documents")
    st.markdown(
        "<p style='color:#9BA3BC;'>Any ONE of these 12 documents is sufficient to vote.</p>",
        unsafe_allow_html=True,
    )

    docs = rights.get("documents_accepted", [])
    icons = ["🪪", "🆔", "🛂", "🚗", "📋", "🏥", "🏦", "💳", "📱", "👴", "💼", "🏛️"]

    cols = st.columns(3)
    for i, doc in enumerate(docs):
        with cols[i % 3]:
            icon = icons[i] if i < len(icons) else "📄"
            st.markdown(
                f"""<div class="bb-card" style="padding:12px;text-align:center;min-height:80px;">
                <div style="font-size:1.6rem;">{icon}</div>
                <div style="font-size:0.8rem;color:#9BA3BC;margin-top:6px;line-height:1.4;">{doc}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown(
        """<div class="bb-alert bb-alert-warn" style="margin-top:16px;">
        ⚠️ <strong>Important:</strong> If your name has a minor spelling error in the roll,
        you can still vote — show your document and inform the Presiding Officer.
        </div>""",
        unsafe_allow_html=True,
    )


def _render_evm_guide() -> None:
    """Render EVM awareness and VVPAT explainer."""
    st.markdown("### 🗳️ Electronic Voting Machine (EVM) Guide")

    col1, col2 = st.columns([1.2, 1])

    with col1:
        steps = [
            ("Enter the booth", "Your name is verified against the electoral roll by the Presiding Officer."),
            ("Receive voter slip", "A numbered slip is issued — this doesn't reveal your identity."),
            ("Enter the voting compartment", "Complete privacy is ensured. No cameras, no witnesses."),
            ("Press your candidate's button", "A beep confirms your vote is recorded on the EVM."),
            ("Check the VVPAT slip", "A paper slip shows your vote for 7 seconds. Verify it matches your choice."),
            ("Collect the indelible ink mark", "Your left index finger is marked — proof you voted!"),
        ]
        for i, (title, desc) in enumerate(steps, 1):
            st.markdown(
                f"""<div class="bb-step">
                <div class="bb-step-num">{i}</div>
                <div>
                  <div style="font-weight:700;color:#E8EAF0;margin-bottom:3px;">{title}</div>
                  <div class="bb-step-text">{desc}</div>
                </div></div>""",
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown("#### 🔒 Why EVMs Are Secure")
        facts = [
            ("No internet", "EVMs have no WiFi, Bluetooth, or network connectivity of any kind."),
            ("Standalone hardware", "Each unit is a standalone device — no central control."),
            ("VVPAT paper trail", "Physical paper slips are printed for every vote cast."),
            ("Supreme Court verified", "India's Supreme Court upheld EVM integrity multiple times."),
            ("Internationally recognized", "Used since 1999, praised by global election observers."),
        ]
        for icon_text, fact_title, fact_desc in [(("🌐", f[0], f[1])) for f in facts]:
            st.markdown(
                f"""<div class="bb-card" style="padding:12px;margin-bottom:8px;">
                <div style="font-weight:700;color:#4ade80;margin-bottom:3px;">✅ {fact_title}</div>
                <div style="font-size:0.82rem;color:#9BA3BC;">{fact_desc}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown(
            """<div class="bb-alert bb-alert-warn">
            🚨 See something suspicious at a booth?
            Report instantly via <strong>cVIGIL App</strong> or call <strong>1950</strong>.
            Action taken within 100 minutes.
            </div>""",
            unsafe_allow_html=True,
        )


def _render_mcc(rights: dict) -> None:
    """Render Model Code of Conduct explainer."""
    st.markdown("### 📜 Model Code of Conduct (MCC)")
    st.markdown(
        """<p style='color:#9BA3BC;'>The MCC is a set of guidelines issued by the ECI
        to ensure free and fair elections. It kicks in from the date of election announcement
        till the result date.</p>""",
        unsafe_allow_html=True,
    )
    for point in rights.get("model_code_of_conduct_key_points", []):
        st.markdown(
            f"""<div class="bb-card" style="padding:12px;margin-bottom:8px;">
            <div style="display:flex;gap:10px;align-items:flex-start;">
              <span style="color:#FF6B1A;font-size:1.1rem;">⚡</span>
              <div style="color:#E8EAF0;font-size:0.9rem;line-height:1.5;">{point}</div>
            </div></div>""",
            unsafe_allow_html=True,
        )
