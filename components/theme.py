"""
components/theme.py — Design system for Buddhiman Bharat
Saffron (#FF6B1A), White (#FFFFFF), India Green (#138808) palette
"""

DARK_THEME_CSS = """
<style>
/* ── Google Fonts ──────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700;800&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap');

/* ── CSS Variables ─────────────────────────────────────────── */
:root {
  --saffron: #FF6B1A;
  --saffron-light: #FF8C47;
  --saffron-dim: rgba(255, 107, 26, 0.15);
  --india-green: #138808;
  --india-green-light: #1aad0a;
  --india-green-dim: rgba(19, 136, 8, 0.15);
  --navy-wheel: #000080;
  --bg-primary: #0E1117;
  --bg-secondary: #1A1D2E;
  --bg-card: #181B26;
  --bg-card-hover: #1E2235;
  --border: rgba(255,255,255,0.08);
  --border-accent: rgba(255,107,26,0.3);
  --text-primary: #E8EAF0;
  --text-secondary: #9BA3BC;
  --text-muted: #5C6480;
  --radius: 12px;
  --radius-sm: 8px;
  --shadow: 0 4px 24px rgba(0,0,0,0.4);
}

/* ── Global Reset ──────────────────────────────────────────── */
html, body, .stApp { background-color: var(--bg-primary) !important; }
.stApp { font-family: 'DM Sans', 'Noto Sans Devanagari', sans-serif !important; }
h1,h2,h3,h4,h5 { color: var(--text-primary) !important; font-family: 'DM Sans', sans-serif !important; }
p, li, span, div { color: var(--text-primary); }
.stMarkdown p { color: var(--text-secondary); }

/* ── Scrollbar ─────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--saffron); border-radius: 3px; }

/* ── Top Navigation Bar ────────────────────────────────────── */
.bb-topnav {
  display: flex; justify-content: space-between; align-items: center;
  background: linear-gradient(135deg, var(--bg-secondary) 0%, #1E213A 100%);
  border-bottom: 2px solid transparent;
  border-image: linear-gradient(90deg, var(--saffron), var(--india-green)) 1;
  padding: 12px 24px; margin-bottom: 16px;
  position: sticky; top: 0; z-index: 100;
  backdrop-filter: blur(12px);
}
.bb-logo { display: flex; align-items: center; gap: 12px; }
.bb-logo-icon {
  width: 44px; height: 44px; border-radius: 10px;
  background: linear-gradient(135deg, var(--saffron), var(--india-green));
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 1.1rem; color: white; letter-spacing: -1px;
}
.bb-logo-title { font-size: 1.2rem; font-weight: 800; color: var(--text-primary); letter-spacing: -0.5px; }
.bb-logo-sub { font-size: 0.7rem; color: var(--saffron); font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; }

/* ── Live Badge ────────────────────────────────────────────── */
.bb-live-badge {
  display: flex; align-items: center; gap: 8px;
  background: rgba(19,136,8,0.15); border: 1px solid rgba(19,136,8,0.4);
  border-radius: 20px; padding: 6px 14px;
  font-size: 0.75rem; font-weight: 700; color: #4ade80; letter-spacing: 0.06em;
}
.bb-live-dot {
  width: 8px; height: 8px; border-radius: 50%; background: #4ade80;
  animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(1.3)} }

/* ── Tricolour Accent Bar ──────────────────────────────────── */
.bb-tricolour {
  height: 4px;
  background: linear-gradient(90deg, var(--saffron) 33%, white 33% 66%, var(--india-green) 66%);
  margin-bottom: 16px; border-radius: 2px;
}

/* ── Cards ─────────────────────────────────────────────────── */
.bb-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px; margin-bottom: 16px;
  transition: border-color 0.2s, transform 0.2s;
}
.bb-card:hover { border-color: var(--border-accent); transform: translateY(-1px); }
.bb-card-title { font-size: 0.7rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; }
.bb-card-value { font-size: 2rem; font-weight: 800; color: var(--text-primary); line-height: 1; }
.bb-card-sub { font-size: 0.8rem; color: var(--text-secondary); margin-top: 4px; }

/* ── Metric Accent Colors ──────────────────────────────────── */
.bb-metric-saffron .bb-card-value { color: var(--saffron); }
.bb-metric-green .bb-card-value { color: var(--india-green-light); }

/* ── Tabs ──────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg-secondary) !important; border-radius: var(--radius) !important;
  padding: 4px !important; gap: 2px !important; border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important; color: var(--text-secondary) !important;
  border-radius: var(--radius-sm) !important; font-weight: 600 !important;
  font-size: 0.8rem !important; padding: 8px 14px !important;
}
.stTabs [aria-selected="true"] {
  background: var(--saffron) !important; color: white !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 16px !important; }

/* ── Buttons ───────────────────────────────────────────────── */
.stButton > button {
  background: linear-gradient(135deg, var(--saffron), #e05a12) !important;
  color: white !important; border: none !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 700 !important; font-size: 0.88rem !important;
  transition: all 0.2s !important;
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(255,107,26,0.4) !important; }
.stButton > button[kind="secondary"] {
  background: var(--bg-card) !important; color: var(--text-secondary) !important;
  border: 1px solid var(--border) !important;
}

/* ── Inputs ────────────────────────────────────────────────── */
.stTextInput input, .stSelectbox select, .stTextArea textarea {
  background: var(--bg-card) !important; border: 1px solid var(--border) !important;
  color: var(--text-primary) !important; border-radius: var(--radius-sm) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--saffron) !important;
  box-shadow: 0 0 0 2px var(--saffron-dim) !important;
}

/* ── Chat Messages ─────────────────────────────────────────── */
.stChatMessage { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; }

/* ── Progress / Steps ──────────────────────────────────────── */
.bb-step {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 12px 0; border-bottom: 1px solid var(--border);
}
.bb-step-num {
  width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
  background: var(--saffron); color: white;
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 0.8rem;
}
.bb-step-done .bb-step-num { background: var(--india-green); }
.bb-step-text { font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5; }

/* ── Party Pill ────────────────────────────────────────────── */
.bb-party-pill {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px; border-radius: 20px; font-size: 0.75rem;
  font-weight: 700; border: 1px solid currentColor;
}

/* ── Alert Boxes ───────────────────────────────────────────── */
.bb-alert { padding: 12px 16px; border-radius: var(--radius-sm); margin: 8px 0; font-size: 0.88rem; }
.bb-alert-info { background: rgba(59,130,246,0.1); border-left: 3px solid #3b82f6; color: #93c5fd; }
.bb-alert-warn { background: rgba(251,191,36,0.1); border-left: 3px solid #fbbf24; color: #fde68a; }
.bb-alert-success { background: var(--india-green-dim); border-left: 3px solid var(--india-green); color: #86efac; }
.bb-alert-error { background: rgba(239,68,68,0.1); border-left: 3px solid #ef4444; color: #fca5a5; }

/* ── Verdict Badge ─────────────────────────────────────────── */
.verdict-true { color: #ef4444; font-weight: 700; }
.verdict-misleading { color: #fbbf24; font-weight: 700; }
.verdict-false { color: #86efac; font-weight: 700; }

/* ── Footer ────────────────────────────────────────────────── */
.bb-footer {
  text-align: center; padding: 24px 0; margin-top: 32px;
  border-top: 1px solid var(--border);
  color: var(--text-muted); font-size: 0.75rem;
}

/* ── Sidebar ───────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--bg-secondary) !important;
  border-right: 1px solid var(--border) !important;
}

/* ── Metric Overrides ──────────────────────────────────────── */
[data-testid="stMetric"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important; padding: 16px !important;
}
[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 0.75rem !important; }
[data-testid="stMetricValue"] { color: var(--text-primary) !important; }

/* ── Expander ──────────────────────────────────────────────── */
.streamlit-expanderHeader {
  background: var(--bg-card) !important; border-radius: var(--radius-sm) !important;
  color: var(--text-primary) !important;
}

/* ── Divider ───────────────────────────────────────────────── */
hr { border-color: var(--border) !important; }
</style>
"""

ACCESSIBILITY_CSS = """
<style>
/* WCAG 2.1 AA Accessibility */
:focus-visible { outline: 3px solid var(--saffron) !important; outline-offset: 2px !important; }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); border: 0; }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; } }
@media (prefers-contrast: high) { :root { --border: rgba(255,255,255,0.3); --text-secondary: #C8CADC; } }
</style>
"""

SKIP_LINK_HTML = """
<a href="#main-content" class="sr-only" style="
  position:fixed;top:8px;left:8px;background:var(--saffron);color:white;
  padding:8px 16px;border-radius:4px;z-index:9999;text-decoration:none;font-weight:700;
  display:none;
" onfocus="this.style.display='block'" onblur="this.style.display='none'">
  Skip to main content
</a>
"""
