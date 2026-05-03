"""
components/voter_feedback.py — Voter feedback form backed by Google Sheets,
plus live election update notifications from Google Sheets.
"""

import streamlit as st
from config.settings import INDIA
from services.google_sheets import (
    append_feedback_row,
    get_election_updates_from_sheet,
    build_voter_feedback_form_url,
)
from utils.validators import validate_feedback


def render_feedback_form() -> None:
    """Render anonymous voter feedback form that writes to Google Sheets."""
    st.markdown("### 💬 Share Your Experience")
    st.markdown(
        "<p style='color:#9BA3BC;font-size:0.85rem;'>Help us improve — your feedback is "
        "anonymous and goes directly to our team via Google Sheets.</p>",
        unsafe_allow_html=True,
    )

    with st.form("voter_feedback_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "First name (optional)",
                placeholder="e.g. Rahul",
                max_chars=50,
                help="Leave blank to stay anonymous",
            )

        with col2:
            state = st.session_state.get("election_data", {}).get("state", "India") \
                if st.session_state.get("election_data") else "India"
            st.text_input("Your state", value=state, disabled=True)

        rating = st.select_slider(
            "Rate this app ⭐",
            options=[1, 2, 3, 4, 5],
            value=5,
            format_func=lambda x: "⭐" * x,
            help="1 = Poor, 5 = Excellent",
        )

        feedback_text = st.text_area(
            "Your feedback",
            placeholder="What did you find most helpful? Any suggestions?",
            max_chars=300,
            height=100,
        )

        submitted = st.form_submit_button(
            "📤 Submit Feedback",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            is_valid, sanitized = validate_feedback(feedback_text or "No comment")
            if not is_valid:
                st.error("Please enter at least a few words of feedback.")
            else:
                success = append_feedback_row(
                    name=name or "Anonymous",
                    state=state,
                    rating=rating,
                    feedback=sanitized,
                )
                if success:
                    st.success("🙏 Thank you! Your feedback has been recorded.")
                else:
                    # Fallback to Google Form if Sheets webhook not configured
                    form_url = build_voter_feedback_form_url(state)
                    st.info(
                        f"Feedback saved locally. You can also submit via our "
                        f"[Google Form]({form_url}) for a detailed response."
                    )

    # Alternative: direct Google Form link
    form_url = build_voter_feedback_form_url(
        st.session_state.get("election_data", {}).get("state", "") 
        if st.session_state.get("election_data") else ""
    )
    st.markdown(
        f'<p style="font-size:0.78rem;color:#5C6480;margin-top:4px;">'
        f'Prefer a form? <a href="{form_url}" target="_blank" style="color:#FF6B1A;">'
        f'Open Google Form →</a></p>',
        unsafe_allow_html=True,
    )


def render_election_notifications(sheet_id: str = "") -> None:
    """
    Fetch live election updates from Google Sheets and display as notifications.
    Gracefully shows nothing if Sheets is not configured.
    """
    updates = get_election_updates_from_sheet(sheet_id)
    state_code = st.session_state.get("state_code", "")

    if not updates:
        return  # Silent — don't clutter UI if no updates

    # Filter to this state + national updates
    relevant = [
        u for u in updates
        if u.get("state", "").upper() in ("INDIA", "ALL", state_code, "")
        or state_code == ""
    ][:3]  # Max 3 notifications

    if not relevant:
        return

    st.markdown("#### 🔔 Live Election Updates")
    for update in relevant:
        priority = update.get("priority", "normal")
        alert_class = "bb-alert-warn" if priority == "high" else "bb-alert-info"
        icon = "🚨" if priority == "high" else "📢"

        st.markdown(
            f"""<div class="bb-alert {alert_class}" style="margin-bottom:8px;">
            {icon} <strong>{update.get('title', '')}</strong>
            <span style="color:#9BA3BC;font-size:0.75rem;float:right;">{update.get('timestamp', '')}</span>
            <br><span style="font-size:0.85rem;">{update.get('body', '')}</span>
            </div>""",
            unsafe_allow_html=True,
        )
