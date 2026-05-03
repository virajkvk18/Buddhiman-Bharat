"""
components/results_dashboard.py — Live election results with interactive Plotly charts
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from config.settings import PARTIES
from services.election_api import get_national_result_summary, get_state_assembly_history


def render_results_dashboard(state_code: str = "", state_name: str = "India") -> None:
    """Render election results tab."""
    st.markdown(f"## 📊 Election Results — {state_name}")

    tab_lok, tab_assembly, tab_trends = st.tabs(
        ["🇮🇳 Lok Sabha 2024", "🏛️ Assembly Elections", "📈 Historical Trends"]
    )

    with tab_lok:
        _render_lok_sabha_results()

    with tab_assembly:
        _render_assembly_results()

    with tab_trends:
        _render_state_trends(state_code)


def _render_lok_sabha_results() -> None:
    """Render 2024 Lok Sabha national results."""
    data = get_national_result_summary()
    if not data:
        st.info("Election data loading…")
        return

    results = data.get("results", {})

    # Headline metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Seats", data.get("total_seats", 543))
    with col2:
        st.metric("Voter Turnout", f"{data.get('turnout_percent', 0):.1f}%")
    with col3:
        st.metric("Phases", data.get("phases", 7))
    with col4:
        st.metric("Result Date", data.get("result_date", "Jun 4, 2024"))

    st.markdown("---")

    # Donut chart
    col_chart, col_table = st.columns([1.2, 1])

    with col_chart:
        labels, values, colors = [], [], []
        party_colors = {
            "BJP": "#FF6B00", "INC": "#00A3E0", "SP": "#FF0000",
            "TMC": "#29ABE2", "DMK": "#CC0000", "TDP": "#FFFF00",
            "JDU": "#00A86B", "Others": "#5C6480",
        }
        for party, res in results.items():
            labels.append(party)
            values.append(res["seats"])
            colors.append(party_colors.get(party, "#888"))

        fig = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.55,
            marker=dict(colors=colors, line=dict(color="#0E1117", width=2)),
            textinfo="label+value",
            textfont=dict(size=12, color="white"),
            hovertemplate="<b>%{label}</b><br>Seats: %{value}<br>Share: %{percent}<extra></extra>",
        ))
        fig.add_annotation(
            text="<b>543</b><br>Seats",
            x=0.5, y=0.5, font_size=16, showarrow=False,
            font=dict(color="white"),
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"), showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10), height=320,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.markdown("#### Party-wise Seats")
        for party, res in sorted(results.items(), key=lambda x: -x[1]["seats"]):
            seats = res["seats"]
            vote_share = res["vote_share"]
            bar_pct = int(seats / 543 * 100)
            color = party_colors.get(party, "#888")
            st.markdown(
                f"""<div style="margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                  <span style="font-weight:700;color:#E8EAF0;">{party}</span>
                  <span style="color:#9BA3BC;">{seats} seats · {vote_share}%</span>
                </div>
                <div style="background:#1A1D2E;border-radius:4px;height:8px;overflow:hidden;">
                  <div style="width:{bar_pct}%;height:100%;background:{color};border-radius:4px;"></div>
                </div></div>""",
                unsafe_allow_html=True,
            )

        # Majority line info
        st.markdown(
            """<div class="bb-alert bb-alert-info" style="margin-top:12px;">
            🏛️ <strong>Majority mark: 272 seats</strong><br>
            NDA won 293 seats (BJP 240 + allies). 
            Narendra Modi sworn in as PM for third term.
            </div>""",
            unsafe_allow_html=True,
        )


def _render_assembly_results() -> None:
    """Render 2024 state assembly election results."""
    assembly_results = [
        {"state": "Andhra Pradesh", "winner": "TDP+BJP+JSP", "seats": 164, "total": 175, "month": "Jun 2024"},
        {"state": "Haryana", "winner": "BJP", "seats": 48, "total": 90, "month": "Oct 2024"},
        {"state": "J&K", "winner": "NC+INC", "seats": 49, "total": 90, "month": "Oct 2024"},
        {"state": "Maharashtra", "winner": "Mahayuti", "seats": 230, "total": 288, "month": "Nov 2024"},
        {"state": "Jharkhand", "winner": "INDIA Alliance", "seats": 56, "total": 81, "month": "Nov 2024"},
    ]

    for result in assembly_results:
        pct = result["seats"] / result["total"] * 100
        col_info, col_bar = st.columns([1.5, 2])
        with col_info:
            st.markdown(
                f"""<div class="bb-card" style="padding:14px;">
                <div class="bb-card-title">{result['month']}</div>
                <div style="font-weight:800;font-size:1.1rem;color:#E8EAF0;">{result['state']}</div>
                <div style="color:#FF6B1A;font-weight:700;margin-top:4px;">
                  🏆 {result['winner']}
                </div>
                <div style="color:#9BA3BC;font-size:0.8rem;">{result['seats']} / {result['total']} seats ({pct:.0f}%)</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col_bar:
            fig = go.Figure(go.Bar(
                x=[result["seats"], result["total"] - result["seats"]],
                y=[""], orientation="h",
                marker_color=["#FF6B1A", "#1A1D2E"],
                text=[f"{result['seats']}", ""],
                textposition="inside",
                hoverinfo="skip",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                barmode="stack", height=60, margin=dict(t=5, b=5, l=0, r=0),
                xaxis=dict(showticklabels=False, showgrid=False),
                yaxis=dict(showticklabels=False, showgrid=False),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)


def _render_state_trends(state_code: str) -> None:
    """Render historical election trends for a state."""
    history = get_state_assembly_history(state_code)

    if not history:
        st.info("Select a specific state to see historical election trends.")
        # Show national turnout trend instead
        years = [2009, 2014, 2019, 2024]
        turnout = [58.2, 66.4, 67.4, 65.8]
        fig = px.line(
            x=years, y=turnout,
            title="National Voter Turnout — Lok Sabha Elections (%)",
            markers=True, line_shape="spline",
        )
        fig.update_traces(line_color="#FF6B1A", marker_color="#FF6B1A", marker_size=10)
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"), xaxis=dict(color="white"),
            yaxis=dict(color="white", range=[50, 75]),
            title_font=dict(color="white"),
        )
        st.plotly_chart(fig, use_container_width=True)
        return

    years = [h["year"] for h in history]
    turnout = [h.get("turnout", 0) for h in history]
    winners = [h["winner"] for h in history]
    winner_seats = [h["seats"] for h in history]
    total_seats = history[0]["total"]

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            x=years, y=winner_seats,
            title="Winning Party Seats by Election",
            labels={"x": "Year", "y": "Seats Won"},
            color=winner_seats,
            color_continuous_scale=["#138808", "#FF6B1A"],
            text=winners,
        )
        fig.add_hline(y=total_seats // 2 + 1, line_dash="dot", line_color="#fbbf24",
                      annotation_text="Majority", annotation_font_color="#fbbf24")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"), coloraxis_showscale=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.line(
            x=years, y=turnout, title="Voter Turnout Trend (%)",
            markers=True, line_shape="spline",
        )
        fig2.update_traces(line_color="#4ade80", marker_color="#4ade80", marker_size=10)
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"), yaxis=dict(range=[50, 90]),
        )
        st.plotly_chart(fig2, use_container_width=True)
