"""
components/fake_news_checker.py — Election fake news / misinformation checker
"""

import streamlit as st
from services.fact_check import check_claim, KNOWN_MISINFORMATION
from config.settings import INDIA


def render_fake_news_checker() -> None:
    """Render the Fake News Checker tab."""
    st.markdown("## 🔍 Election Fake News Checker")
    st.markdown(
        """<p style='color:#9BA3BC;'>
        India faces a flood of election misinformation every cycle.
        Paste any claim, rumour, or WhatsApp forward to verify it.
        </p>""",
        unsafe_allow_html=True,
    )

    # Input
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        claim_input = st.text_area(
            "Paste the claim or rumour here",
            placeholder="e.g. 'EVMs can be hacked via Bluetooth' or 'Aadhaar is compulsory to vote'",
            height=100,
            max_chars=500,
            label_visibility="collapsed",
        )
    with col_btn:
        st.markdown("<div style='height:42px;'></div>", unsafe_allow_html=True)
        check_clicked = st.button("🔍 Check Claim", type="primary", use_container_width=True)

    if check_clicked and claim_input.strip():
        _render_fact_result(claim_input.strip())

    # Common myths section
    st.markdown("---")
    st.markdown("### 🚫 Common Election Myths — Busted")
    _render_myth_busters()

    # Tips
    st.markdown("---")
    _render_verification_tips()


def _render_fact_result(claim: str) -> None:
    """Display fact-check result for a given claim."""
    with st.spinner("Checking with ECI database and Google Fact Check…"):
        result = check_claim(claim)

    if not result or not result.get("found"):
        st.markdown(
            f"""<div class="bb-alert bb-alert-warn">
            🔍 <strong>Claim not found in our database.</strong><br>
            We couldn't verify this specific claim automatically. Please:
            <ul style="margin-top:8px;color:#9BA3BC;">
              <li>Check <strong>eci.gov.in</strong> for official information</li>
              <li>Call <strong>{INDIA['VOTER_HELPLINE']}</strong> for election-related clarifications</li>
              <li>Verify on <strong>factcheck.afp.com</strong> or <strong>altnews.in</strong></li>
            </ul>
            </div>""",
            unsafe_allow_html=True,
        )
        return

    verdict = result.get("verdict", "")
    verdict_upper = verdict.upper()

    verdict_config = {
        "FALSE": ("✅", "#86efac", "bb-alert-success", "This claim is FALSE. Good news — it's misinformation!"),
        "TRUE": ("❌", "#fca5a5", "bb-alert-error", "This claim appears TRUE. Concerning if it relates to malpractice."),
        "MISLEADING": ("⚠️", "#fde68a", "bb-alert-warn", "This claim is MISLEADING. It contains partial truths."),
    }

    icon, color, alert_class, summary = verdict_config.get(
        verdict_upper, ("❓", "#9BA3BC", "bb-alert-info", "Verdict unclear.")
    )

    st.markdown(
        f"""<div class="bb-alert {alert_class}" style="margin-bottom:16px;">
        <div style="font-size:1.1rem;font-weight:800;margin-bottom:8px;">{icon} Verdict: <span style="color:{color};">{verdict}</span></div>
        <div style="font-weight:700;margin-bottom:6px;">Claim: "{result.get('claim', claim)[:120]}…"</div>
        <div style="margin-bottom:8px;line-height:1.6;">{result.get('explanation', summary)}</div>
        <div style="font-size:0.78rem;color:#9BA3BC;">
          📚 Source: <strong>{result.get('cited_source', 'Buddhiman Bharat Database')}</strong>
          {' · <a href="' + result['url'] + '" target="_blank" style="color:#FF6B1A;">Read more →</a>' if result.get('url') else ''}
        </div>
        </div>""",
        unsafe_allow_html=True,
    )


def _render_myth_busters() -> None:
    """Display known election myths in expandable cards."""
    for myth in KNOWN_MISINFORMATION:
        verdict = myth["verdict"]
        verdict_color = {"FALSE": "#86efac", "MISLEADING": "#fde68a", "TRUE": "#fca5a5"}.get(verdict, "#9BA3BC")
        with st.expander(f"❓ Myth: {myth['claim']}"):
            st.markdown(
                f"""<div style="padding:8px 0;">
                <div style="font-weight:800;color:{verdict_color};font-size:1rem;margin-bottom:8px;">
                  Verdict: {verdict}
                </div>
                <div style="color:#E8EAF0;line-height:1.6;">{myth['explanation']}</div>
                <div style="margin-top:8px;font-size:0.78rem;color:#9BA3BC;">📚 {myth['source']}</div>
                </div>""",
                unsafe_allow_html=True,
            )


def _render_verification_tips() -> None:
    """Tips for voters to spot misinformation."""
    st.markdown("### 💡 How to Spot Election Fake News")
    tips = [
        ("🔗", "Check the URL", "Fake sites often mimic real ones with slight spelling changes (e.g., ec1.gov.in instead of eci.gov.in)."),
        ("📅", "Check the date", "Old news often circulates as 'new'. Verify when the content was originally published."),
        ("📸", "Reverse image search", "Use Google Lens or TinEye to check if photos are from a different event or context."),
        ("📞", "Call ECI Helpline", f"When in doubt, call {INDIA['VOTER_HELPLINE']} — it's toll-free and 24x7 during elections."),
        ("🤳", "Don't forward without checking", "The cVIGIL App lets you report suspicious content geo-tagged to your location."),
        ("📰", "Cross-check sources", "Verify claims on at least 2 credible sources: ECI, PIB, or established news outlets."),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(tips):
        with cols[i % 3]:
            st.markdown(
                f"""<div class="bb-card" style="padding:14px;min-height:120px;">
                <div style="font-size:1.5rem;margin-bottom:8px;">{icon}</div>
                <div style="font-weight:700;color:#E8EAF0;margin-bottom:6px;font-size:0.9rem;">{title}</div>
                <div style="color:#9BA3BC;font-size:0.8rem;line-height:1.5;">{desc}</div>
                </div>""",
                unsafe_allow_html=True,
            )
