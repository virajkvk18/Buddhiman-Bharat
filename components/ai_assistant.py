"""
components/ai_assistant.py
Full-featured AI Voter Assistant chatbot with:
  - Gemini streaming responses
  - Typing indicator
  - Message timestamps
  - Chat history export
  - Quick-suggestion chips
  - Auto fact-check overlay
  - No-API fallback cards
"""

import streamlit as st
from datetime import datetime
from config.settings import GOOGLE_API_KEY, INDIA, MAX_AI_QUERIES
from services.gemini_service import (
    call_gemini_streaming,
    get_quick_answers,
    detect_language_from_text,
    GREETING_MESSAGE,
)
from services.fact_check import check_claim, is_election_claim
from components.language_selector import T

# ── Chatbot CSS ───────────────────────────────────────────────────────────────
CHATBOT_CSS = """
<style>
/* Chat container full-height feel */
.chat-wrapper {
  display: flex; flex-direction: column;
  background: #12151F;
  border: 1px solid rgba(255,107,26,0.2);
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 12px;
}

/* Chat header */
.chat-header {
  background: linear-gradient(135deg, #1A1D2E, #1E2235);
  padding: 14px 20px;
  display: flex; align-items: center; gap: 12px;
  border-bottom: 1px solid rgba(255,107,26,0.2);
}
.chat-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: linear-gradient(135deg, #FF6B1A, #138808);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem; flex-shrink: 0;
}
.chat-header-info { flex: 1; }
.chat-header-name { font-weight: 800; color: #E8EAF0; font-size: 0.95rem; }
.chat-header-status {
  font-size: 0.72rem; color: #4ade80;
  display: flex; align-items: center; gap: 5px;
}
.status-dot {
  width: 7px; height: 7px; border-radius: 50%; background: #4ade80;
  animation: pulse 2s infinite;
}

/* Message bubbles */
.msg-row { display: flex; gap: 10px; padding: 8px 16px; align-items: flex-end; }
.msg-row.user { flex-direction: row-reverse; }
.msg-avatar {
  width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; font-size: 0.9rem;
}
.msg-avatar.bot { background: linear-gradient(135deg, #FF6B1A, #138808); }
.msg-avatar.user { background: linear-gradient(135deg, #3b82f6, #8b5cf6); }
.bubble {
  max-width: 80%; padding: 10px 14px; border-radius: 16px;
  font-size: 0.88rem; line-height: 1.6;
}
.bubble.bot {
  background: #1E2235; color: #E8EAF0;
  border-bottom-left-radius: 4px;
  border: 1px solid rgba(255,255,255,0.06);
}
.bubble.user {
  background: linear-gradient(135deg, #FF6B1A, #e05a12);
  color: white; border-bottom-right-radius: 4px;
}
.msg-time { font-size: 0.65rem; color: #5C6480; margin-top: 4px; text-align: right; }
.msg-time.bot-time { text-align: left; }

/* Typing indicator */
.typing-indicator {
  display: flex; gap: 5px; align-items: center; padding: 4px 0;
}
.typing-dot {
  width: 7px; height: 7px; border-radius: 50%; background: #FF6B1A;
  animation: bounce 1.2s infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%,80%,100%{transform:translateY(0)} 40%{transform:translateY(-6px)} }

/* Suggestion chips */
.chips-wrap { display: flex; flex-wrap: wrap; gap: 8px; padding: 10px 16px 12px; }
.chip {
  background: rgba(255,107,26,0.1); border: 1px solid rgba(255,107,26,0.3);
  color: #FF8C47; border-radius: 20px; padding: 5px 12px;
  font-size: 0.75rem; font-weight: 600; cursor: pointer;
  transition: all 0.2s;
}
.chip:hover { background: rgba(255,107,26,0.2); border-color: #FF6B1A; }

/* Fact-check badge inside chat */
.fc-badge {
  margin-top: 8px; padding: 8px 12px;
  background: rgba(251,191,36,0.08); border-left: 3px solid #fbbf24;
  border-radius: 0 8px 8px 0; font-size: 0.78rem; color: #fde68a;
}

/* Export / clear buttons */
.chat-actions {
  display: flex; gap: 8px; padding: 10px 16px;
  border-top: 1px solid rgba(255,255,255,0.06);
  background: #12151F;
}

/* Query counter badge */
.query-counter {
  background: rgba(255,107,26,0.12); border: 1px solid rgba(255,107,26,0.25);
  border-radius: 12px; padding: 4px 10px;
  font-size: 0.72rem; font-weight: 700; color: #FF8C47;
}
</style>
"""


# ── Public render function ────────────────────────────────────────────────────

def render_ai_assistant(election_data: dict) -> None:
    """Render the full AI Voter Assistant chatbot."""
    st.markdown(CHATBOT_CSS, unsafe_allow_html=True)

    # Ensure greeting on first load
    if "ai_messages" not in st.session_state or not st.session_state["ai_messages"]:
        st.session_state["ai_messages"] = [{
            "role": "assistant",
            "content": GREETING_MESSAGE,
            "ts": _now(),
        }]

    remaining = MAX_AI_QUERIES - st.session_state.get("ai_query_count", 0)

    # ── Chat header ──────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="chat-wrapper">
          <div class="chat-header">
            <div class="chat-avatar" aria-hidden="true">🤖</div>
            <div class="chat-header-info">
              <div class="chat-header-name">Buddhiman Bharat AI</div>
              <div class="chat-header-status">
                <div class="status-dot"></div>
                {'Online · Powered by Gemini 1.5 Flash' if GOOGLE_API_KEY else 'Configure GOOGLE_API_KEY to enable AI'}
              </div>
            </div>
            <div class="query-counter" title="Queries remaining this session">{remaining} left</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── No API key warning ───────────────────────────────────────────────────
    if not GOOGLE_API_KEY:
        st.markdown(
            """
            <div class="bb-alert bb-alert-warn" style="margin-bottom:12px;">
            ⚠️ <strong>Gemini API key not set.</strong>
            Add <code>GOOGLE_API_KEY=your_key</code> to your <code>.env</code> file
            (or Hugging Face → Settings → Secrets).<br>
            Get a free key at <a href="https://aistudio.google.com" target="_blank"
            style="color:#FF6B1A;">aistudio.google.com</a>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _render_fallback_cards()
        return

    # ── Render chat messages ─────────────────────────────────────────────────
    _render_chat_history()

    # ── Suggestion chips (only when few messages) ────────────────────────────
    msg_count = len(st.session_state.get("ai_messages", []))
    if msg_count <= 3:
        _render_suggestion_chips(election_data)

    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

    # ── Action bar: Clear / Export ───────────────────────────────────────────
    _render_action_bar()

    # ── Query limit guard ────────────────────────────────────────────────────
    if remaining <= 0:
        st.error(
            f"⚠️ Session limit reached ({MAX_AI_QUERIES} queries). "
            f"Refresh the page to continue.\n\n"
            f"ECI Helpline: **{INDIA['VOTER_HELPLINE']}**"
        )
        return

    # ── Chat input ───────────────────────────────────────────────────────────
    placeholder = T("Ask about voting, registration, booth…")
    if user_input := st.chat_input(placeholder, key="main_chat_input"):
        _handle_query(user_input, election_data)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now().strftime("%I:%M %p")


def _render_chat_history() -> None:
    """Render all messages in the chat history."""
    messages = st.session_state.get("ai_messages", [])

    for msg in messages:
        role = msg["role"]
        content = msg.get("content", "")
        ts = msg.get("ts", "")
        fact = msg.get("fact_check")

        if role == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(content)
                if ts:
                    st.markdown(f"<div class='msg-time'>{ts}</div>", unsafe_allow_html=True)
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(content)
                if fact and fact.get("found"):
                    _render_inline_fact_badge(fact)
                if ts:
                    st.markdown(f"<div class='msg-time bot-time'>{ts}</div>", unsafe_allow_html=True)


def _handle_query(q: str, election_data: dict) -> None:
    """Validate, store, and stream response for a user query."""
    from utils.validators import validate_ai_query

    is_valid, sanitized = validate_ai_query(q)
    if not is_valid:
        st.warning("⚠️ Please enter a valid election-related question (2–500 characters).")
        return

    # Auto-detect language
    detected = detect_language_from_text(q)
    if detected != "en":
        st.session_state["language"] = detected

    ts = _now()
    st.session_state["ai_messages"].append({"role": "user", "content": q, "ts": ts})

    # Display user message immediately
    with st.chat_message("user", avatar="👤"):
        st.markdown(q)
        st.markdown(f"<div class='msg-time'>{ts}</div>", unsafe_allow_html=True)

    # Try quick answer first (no API call)
    quick = get_quick_answers(sanitized)
    fact_data = None

    with st.chat_message("assistant", avatar="🤖"):
        if quick:
            st.markdown(quick)
            response_text = quick
        else:
            # Stream from Gemini
            response_text = _stream_response(sanitized, election_data)

            # Auto fact-check if claim detected
            if is_election_claim(sanitized):
                fact_data = check_claim(sanitized)
                if fact_data and fact_data.get("found"):
                    _render_inline_fact_badge(fact_data)

        bot_ts = _now()
        st.markdown(f"<div class='msg-time bot-time'>{bot_ts}</div>", unsafe_allow_html=True)

    st.session_state["ai_messages"].append({
        "role": "assistant",
        "content": response_text,
        "ts": bot_ts,
        "fact_check": fact_data,
    })
    st.session_state["ai_query_count"] = st.session_state.get("ai_query_count", 0) + 1


def _stream_response(question: str, election_data: dict) -> str:
    """Stream Gemini response token by token. Returns full text."""
    history = [
        m for m in st.session_state.get("ai_messages", [])
        if m["role"] in ("user", "assistant")
    ]

    full_text = ""
    placeholder = st.empty()
    placeholder.markdown(
        "<div class='typing-indicator'>"
        "<div class='typing-dot'></div><div class='typing-dot'></div><div class='typing-dot'></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    try:
        for chunk in call_gemini_streaming(
            question=question,
            history=history,
            election_data=election_data,
            state_code=st.session_state.get("state_code", ""),
            language=st.session_state.get("language", "en"),
        ):
            full_text += chunk
            placeholder.markdown(full_text + "▌")

        placeholder.markdown(full_text)
    except Exception:
        # Fallback to non-streaming
        from services.gemini_service import call_gemini
        full_text = call_gemini(
            question=question,
            history=history,
            election_data=election_data,
            state_code=st.session_state.get("state_code", ""),
            language=st.session_state.get("language", "en"),
        )
        placeholder.markdown(full_text)

    return full_text


def _render_inline_fact_badge(fact_data: dict) -> None:
    """Render a compact fact-check badge inside the chat bubble."""
    verdict = fact_data.get("verdict", "").upper()
    colors = {"FALSE": "#86efac", "TRUE": "#fca5a5", "MISLEADING": "#fde68a"}
    color = colors.get(verdict, "#9BA3BC")

    st.markdown(
        f"""<div class="fc-badge">
        🔍 <strong>Fact Check:</strong>
        <span style="color:{color};font-weight:700;">{verdict}</span> —
        {fact_data.get("explanation", "")[:120]}
        <span style="color:#5C6480;"> · {fact_data.get("cited_source", "")}</span>
        </div>""",
        unsafe_allow_html=True,
    )


def _render_suggestion_chips(election_data: dict) -> None:
    """Render clickable suggestion chips below chat when conversation is new."""
    suggestions = [
        "How do I check my voter ID? 🪪",
        "Where is my polling booth? 📍",
        "What is NOTA? 🗳️",
        "Is EVM tamper-proof? 🔒",
        "Name missing from rolls — what to do? 📋",
        "What documents can I use to vote? 📄",
        "How to register as a new voter? ✍️",
        "What is the ECI helpline? 📞",
    ]

    st.markdown(
        "<p style='font-size:0.75rem;color:#5C6480;margin:8px 0 4px;font-weight:600;"
        "text-transform:uppercase;letter-spacing:0.07em;'>💡 Quick questions</p>",
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    for i, s in enumerate(suggestions):
        with cols[i % 4]:
            if st.button(s, key=f"chip_{i}", use_container_width=True, help=s):
                _handle_query(s, election_data)
                st.rerun()


def _render_action_bar() -> None:
    """Render Clear Chat and Export Chat buttons."""
    col_clear, col_export, col_spacer = st.columns([1, 1.5, 4])

    with col_clear:
        if st.button("🗑️ Clear Chat", key="clear_chat", help="Clear conversation history"):
            st.session_state["ai_messages"] = [{
                "role": "assistant",
                "content": GREETING_MESSAGE,
                "ts": _now(),
            }]
            st.session_state["ai_query_count"] = 0
            st.rerun()

    with col_export:
        transcript = _build_transcript()
        if transcript:
            st.download_button(
                label="⬇️ Export Chat",
                data=transcript,
                file_name=f"buddhiman_bharat_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                key="export_chat",
                help="Download this conversation",
            )


def _build_transcript() -> str:
    """Build a plain-text transcript of the conversation."""
    messages = st.session_state.get("ai_messages", [])
    if not messages:
        return ""

    lines = [
        "Buddhiman Bharat — AI Election Assistant",
        "Chat Export",
        f"Date: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
        "=" * 50,
        "",
    ]
    for msg in messages:
        role_label = "You" if msg["role"] == "user" else "Buddhiman Bharat"
        ts = msg.get("ts", "")
        lines.append(f"[{ts}] {role_label}:")
        lines.append(msg.get("content", ""))
        lines.append("")

    lines += [
        "=" * 50,
        f"ECI Helpline: {INDIA['VOTER_HELPLINE']}",
        "eci.gov.in | voterportal.eci.gov.in",
    ]
    return "\n".join(lines)


def _render_fallback_cards() -> None:
    """Show static quick-help cards when Gemini is not configured."""
    st.markdown("### 📚 Quick Voter Help")
    faqs = [
        ("🪪", "Download Voter ID",   "Visit **nvsp.in** or call **1950** for your e-EPIC card."),
        ("📍", "Find Your Booth",     "SMS EPIC number to **1950** or visit **voterportal.eci.gov.in**."),
        ("📋", "Register to Vote",    "Visit **voterportal.eci.gov.in** → New Registration (Form 6)."),
        ("🚨", "Report a Violation",  "Use **cVIGIL App** or call **1950** — action within 100 min."),
        ("🗳️", "Voting Day Tips",    "Carry photo ID, arrive early, check indelible ink on left finger."),
        ("📞", "ECI Helpline",         "Call **1950** (toll-free, 24x7 during elections)."),
    ]
    cols = st.columns(3)
    for i, (icon, title, body) in enumerate(faqs):
        with cols[i % 3]:
            st.markdown(
                f"""<div class="bb-card" style="padding:16px;min-height:110px;">
                <div style="font-size:1.8rem;margin-bottom:8px;">{icon}</div>
                <div style="font-weight:700;color:#E8EAF0;margin-bottom:5px;font-size:0.9rem;">{title}</div>
                <div style="font-size:0.82rem;color:#9BA3BC;line-height:1.5;">{body}</div>
                </div>""",
                unsafe_allow_html=True,
            )
