"""
components/manifesto_analyzer.py — AI-powered party manifesto comparison
"""

import streamlit as st
from config.settings import PARTIES, GOOGLE_API_KEY
from services.gemini_service import call_gemini

MANIFESTO_HIGHLIGHTS = {
    "BJP": {
        "color": "#FF6B00",
        "tagline": "Viksit Bharat @2047",
        "key_promises": [
            "Make India a developed nation by 2047",
            "Build 3 crore affordable homes under PM Awas Yojana",
            "One nation, one election implementation",
            "Uniform Civil Code legislation",
            "Continue 80 crore free ration scheme",
            "Create 2 crore jobs per year in manufacturing",
        ],
        "focus_areas": ["Economy", "Infrastructure", "National Security", "Hindutva"],
    },
    "INC": {
        "color": "#00A3E0",
        "tagline": "Nyay Patra 2024",
        "key_promises": [
            "₹1 lakh per year to every poor family (Mahalaxmi scheme)",
            "30% government jobs reserved for women (Naari Nyay)",
            "Caste census and OBC sub-categorisation",
            "Restore Article 370 debate",
            "Wealth redistribution survey",
            "Apprenticeship of ₹1 lakh for youth",
        ],
        "focus_areas": ["Social Justice", "Employment", "Women Empowerment", "Federalism"],
    },
    "AAP": {
        "color": "#00A5E0",
        "tagline": "Guaranteed Governance",
        "key_promises": [
            "Free electricity up to 300 units nationally",
            "Free quality school education",
            "Free healthcare via Mohalla Clinics",
            "Anti-corruption ombudsman in every state",
            "Women's safety guarantee",
        ],
        "focus_areas": ["Governance", "Education", "Healthcare", "Anti-Corruption"],
    },
    "SP": {
        "color": "#FF0000",
        "tagline": "PDA Alliance",
        "key_promises": [
            "Caste census implementation",
            "75% reservation for UP locals in private jobs",
            "Farm loan waiver",
            "Restore OBC reservation in local bodies",
            "Special status for UP",
        ],
        "focus_areas": ["OBC Rights", "Agriculture", "Employment", "Social Justice"],
    },
    "TMC": {
        "color": "#29ABE2",
        "tagline": "Maa Mati Manush",
        "key_promises": [
            "Federal structure strengthening",
            "State rights against central overreach",
            "Lakshmir Bhandar expansion nationally",
            "Duare Sarkar model for all states",
            "Preserve Bengali culture and identity",
        ],
        "focus_areas": ["Federalism", "Social Schemes", "Cultural Identity", "Women"],
    },
}


def render_manifesto_analyzer() -> None:
    """Render party manifesto comparison and AI summarizer."""
    st.markdown("## 📋 Party Manifesto Analyzer")
    st.markdown(
        "<p style='color:#9BA3BC;'>Compare party promises and get AI-powered neutral summaries.</p>",
        unsafe_allow_html=True,
    )

    # Party selector
    selected_parties = st.multiselect(
        "Select parties to compare (up to 4)",
        options=list(MANIFESTO_HIGHLIGHTS.keys()),
        default=["BJP", "INC"],
        max_selections=4,
        format_func=lambda p: f"{PARTIES.get(p, {}).get('symbol', '')} {PARTIES.get(p, {}).get('name', p)}",
    )

    if not selected_parties:
        st.info("Select at least one party to view its manifesto highlights.")
        return

    # Theme filter
    all_themes = sorted({t for p in MANIFESTO_HIGHLIGHTS.values() for t in p["focus_areas"]})
    selected_theme = st.selectbox("Filter by theme", ["All Themes"] + all_themes)

    st.markdown("---")

    # Manifesto cards
    cols = st.columns(len(selected_parties))
    for i, party_code in enumerate(selected_parties):
        manifesto = MANIFESTO_HIGHLIGHTS.get(party_code, {})
        party_info = PARTIES.get(party_code, {})
        color = manifesto.get("color", "#888")

        with cols[i]:
            promises = manifesto.get("key_promises", [])
            if selected_theme != "All Themes":
                focus = manifesto.get("focus_areas", [])
                if selected_theme not in focus:
                    st.markdown(
                        f"""<div class="bb-card" style="border-top:3px solid {color};opacity:0.4;text-align:center;padding:20px;">
                        <div style="font-size:2rem;">{party_info.get('symbol','')}</div>
                        <div style="color:{color};font-weight:700;">{party_code}</div>
                        <div style="color:#5C6480;font-size:0.8rem;margin-top:8px;">No promises in this theme</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    continue

            st.markdown(
                f"""<div class="bb-card" style="border-top:3px solid {color};">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                  <span style="font-size:1.5rem;">{party_info.get('symbol','')}</span>
                  <div>
                    <div style="font-weight:800;color:{color};">{party_code}</div>
                    <div style="font-size:0.7rem;color:#9BA3BC;">{manifesto.get('tagline','')}</div>
                  </div>
                </div>""",
                unsafe_allow_html=True,
            )
            for promise in promises[:6]:
                st.markdown(
                    f'<div style="font-size:0.82rem;color:#9BA3BC;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
                    f'• {promise}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown(
                f'<div style="margin-top:10px;">' +
                "".join(f'<span class="bb-party-pill" style="color:{color};margin:2px;font-size:0.65rem;">{t}</span>'
                        for t in manifesto.get("focus_areas", [])) +
                '</div></div>',
                unsafe_allow_html=True,
            )

    # AI comparison button
    st.markdown("---")
    if GOOGLE_API_KEY and len(selected_parties) >= 2:
        if st.button("🤖 Get AI Neutral Comparison", type="primary"):
            _render_ai_comparison(selected_parties, selected_theme)
    elif not GOOGLE_API_KEY:
        st.markdown(
            '<div class="bb-alert bb-alert-info">Add GOOGLE_API_KEY to enable AI manifesto comparison.</div>',
            unsafe_allow_html=True,
        )


def _render_ai_comparison(parties: list, theme: str) -> None:
    """Call Gemini to compare manifestos neutrally."""
    manifesto_text = "\n\n".join(
        f"**{p}** ({MANIFESTO_HIGHLIGHTS[p]['tagline']}): "
        + ", ".join(MANIFESTO_HIGHLIGHTS[p]["key_promises"][:4])
        for p in parties if p in MANIFESTO_HIGHLIGHTS
    )

    theme_filter = f" Focus on the theme: {theme}." if theme != "All Themes" else ""
    query = (
        f"Compare these Indian political party manifestos neutrally and factually.{theme_filter} "
        f"Note similarities, differences, and feasibility. Do NOT take sides. Be concise.\n\n{manifesto_text}"
    )

    with st.spinner("Analyzing manifestos with AI…"):
        response = call_gemini(
            question=query,
            history=[],
            election_data={"election_name": "Manifesto Comparison"},
            language="en",
        )

    st.markdown(
        f"""<div class="bb-card" style="border-left:3px solid #FF6B1A;">
        <div style="font-weight:700;color:#FF6B1A;margin-bottom:10px;">🤖 AI Neutral Analysis</div>
        <div style="color:#E8EAF0;font-size:0.9rem;line-height:1.7;">{response}</div>
        <div style="margin-top:10px;font-size:0.7rem;color:#5C6480;">
        ⚠️ AI analysis is for information only. Always read official party manifestos. 
        Buddhiman Bharat does not endorse any political party.
        </div></div>""",
        unsafe_allow_html=True,
    )
