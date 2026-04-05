import streamlit as st
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_loader import (load_main, load_risk_weighted,
                                load_high_risk_prob, get_kpi_metrics,
                                get_yearly_trend, get_cause_contribution)
from utils.charts import (trend_line_chart, yoy_bar_chart,
                          aircraft_bar_chart, top_countries_chart,
                          fatality_severity_donut, monthly_heatmap)
from utils.helpers import format_number, format_pct, yoy_arrow, risk_emoji

st.set_page_config(page_title="Home | Aviation Safety",
                   page_icon="✈️", layout="wide")

# ── Load CSS ────────────────────────────────────
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

# ── Sidebar ─────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding:10px 0 20px 0;'>
            <div style='font-size:2.2rem; margin-bottom:4px;'>&#9992;</div>
            <h3 style='color:#00a8ff; margin:4px 0 0 0; font-family:"Share Tech Mono",monospace;
                        text-shadow:0 0 10px rgba(0,168,255,0.4);'>AVIATION SAFETY</h3>
            <p style='color:#7a8a9a; font-size:0.75rem; margin:0;
                       letter-spacing:3px; text-transform:uppercase;'>
                Intelligence Platform
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("""
        <div style='color:#7a8a9a; font-size:0.8rem; line-height:2;
                    font-family:"Share Tech Mono",monospace;'>
            <span style='color:#00a8ff;'>></span> <b style='color:#e0e0e0;'>DATASET:</b> 2015-2025<br>
            <span style='color:#00a8ff;'>></span> <b style='color:#e0e0e0;'>COVERAGE:</b> GLOBAL<br>
            <span style='color:#00a8ff;'>></span> <b style='color:#e0e0e0;'>RECORDS:</b> 2,596<br>
            <span style='color:#00a8ff;'>></span> <b style='color:#e0e0e0;'>TABLES:</b> 4 (JOINED)<br>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("""
        <div style='color:#7a8a9a; font-size:0.75rem; text-align:center;
                    font-family:"Share Tech Mono",monospace;'>
            THIRD YEAR DATA SCIENCE PROJECT<br>
            <b style='color:#00d4ff;'>TREND ANALYSIS OF GLOBAL<br>AIRPLANE ACCIDENTS</b>
        </div>
    """, unsafe_allow_html=True)

# ── Load Data ────────────────────────────────────
df          = load_main()
risk_w      = load_risk_weighted()
high_risk   = load_high_risk_prob()
kpi         = get_kpi_metrics(df, risk_w, high_risk)
yearly      = get_yearly_trend(df)
cause_df    = get_cause_contribution(df)

# ═══════════════════════════════════════════════
#  HERO SECTION
# ═══════════════════════════════════════════════
st.markdown("""
    <style>
        .hud-hero-frame {
            position: relative;
            text-align: center;
            padding: 40px 20px 20px 20px;
            margin: 0 auto;
            max-width: 900px;
        }
        .hud-hero-frame::before,
        .hud-hero-frame::after {
            content: '';
            position: absolute;
            width: 30px;
            height: 30px;
            border-color: #00a8ff;
            border-style: solid;
            opacity: 0.5;
        }
        .hud-hero-frame::before {
            top: 0; left: 0;
            border-width: 2px 0 0 2px;
        }
        .hud-hero-frame::after {
            top: 0; right: 0;
            border-width: 2px 2px 0 0;
        }
        .hud-hero-bottom::before,
        .hud-hero-bottom::after {
            content: '';
            position: absolute;
            width: 30px;
            height: 30px;
            border-color: #00a8ff;
            border-style: solid;
            opacity: 0.5;
        }
        .hud-hero-bottom::before {
            bottom: 0; left: 0;
            border-width: 0 0 2px 2px;
        }
        .hud-hero-bottom::after {
            bottom: 0; right: 0;
            border-width: 0 2px 2px 0;
        }
        .scanline-overlay {
            pointer-events: none;
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: repeating-linear-gradient(
                0deg,
                transparent,
                transparent 2px,
                rgba(0,168,255,0.015) 2px,
                rgba(0,168,255,0.015) 4px
            );
        }
    </style>
    <div class='hud-hero-frame hud-hero-bottom' style='position:relative;'>
        <div class='scanline-overlay'></div>
        <h1 style='font-size:2.8rem; color:#00a8ff; margin-bottom:8px;
                    font-family:"Share Tech Mono",monospace;
                    text-shadow: 0 0 20px rgba(0,168,255,0.4), 0 0 40px rgba(0,168,255,0.2);
                    letter-spacing:2px;'>
            GLOBAL AVIATION ACCIDENT ANALYSIS
        </h1>
        <p style='font-size:1.1rem; color:#7a8a9a; max-width:700px; margin:0 auto;
                  font-family:"Share Tech Mono",monospace;'>
            A comprehensive trend analysis of worldwide aviation accidents
            from <b style='color:#e0e0e0;'>2015</b> to <b style='color:#e0e0e0;'>2025</b>,
            powered by machine learning and data science.
        </p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# ═══════════════════════════════════════════════
#  ROW 1 — KPI METRICS
# ═══════════════════════════════════════════════
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric("✈️ Total Accidents",
              format_number(kpi["total_accidents"]),
              "2015–2025")
with c2:
    st.metric("💀 Total Fatalities",
              format_number(kpi["total_fatalities"]),
              f"Rate: {kpi['fatality_rate']:.4f}")
with c3:
    st.metric("⚠️ Fatal Accident %",
              format_pct(kpi["fatal_accident_pct"]),
              f"{format_number(kpi['fatal_accidents'])} fatal events",
              delta_color="inverse")
with c4:
    st.metric("📈 Accidents YOY %",
              format_pct(abs(kpi["yoy_pct"])),
              yoy_arrow(kpi["yoy_pct"]),
              delta_color="inverse" if kpi["yoy_pct"] > 0 else "normal")
with c5:
    st.metric("🌍 Highest Risk Country",
              kpi["highest_risk_country"],
              f"{kpi['highest_risk_score']}% risk score",
              delta_color="inverse")

st.divider()

# ═══════════════════════════════════════════════
#  ROW 2 — SECONDARY METRICS
# ═══════════════════════════════════════════════
s1, s2, s3, s4 = st.columns(4)
with s1:
    st.metric("🔥 High Severity Accidents",
              format_number(kpi["high_severity_accidents"]))
with s2:
    st.metric("📊 Damage Severity Index",
              f"{kpi['damage_severity_index']:.3f}",
              "Avg (0=None, 3=Destroyed)")
with s3:
    st.metric("🛫 Commercial Accidents",
              format_number(kpi["commercial_accidents"]),
              "Jet + Turboprop")
with s4:
    st.metric("🛩️ Non-Commercial Accidents",
              format_number(kpi["non_commercial_accidents"]),
              "Private, Cargo, Military")

st.divider()

# ═══════════════════════════════════════════════
#  ROW 3 — TREND CHART + INSIGHTS
# ═══════════════════════════════════════════════
chart_col, insight_col = st.columns([2, 1])

with chart_col:
    st.markdown("""
        <div style='letter-spacing:2px; text-transform:uppercase; color:#00a8ff;
                    font-family:"Share Tech Mono",monospace; font-size:1.1rem;
                    border-bottom:1px solid rgba(0,168,255,0.2); padding-bottom:6px; margin-bottom:10px;'>
            // GLOBAL ACCIDENT TREND
        </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(trend_line_chart(yearly), use_container_width=True)

with insight_col:
    st.markdown("""
        <div style='letter-spacing:2px; text-transform:uppercase; color:#00a8ff;
                    font-family:"Share Tech Mono",monospace; font-size:1.1rem;
                    border-bottom:1px solid rgba(0,168,255,0.2); padding-bottom:6px; margin-bottom:10px;'>
            // KEY INSIGHTS
        </div>
    """, unsafe_allow_html=True)
    insights = [
        ("📉", "Accidents declined significantly from the 2019 peak to 2024"),
        ("✈️", "Most common cause: <b>Runway Excursion</b>"),
        ("🌍", "USA leads globally in total accident count"),
        (risk_emoji(kpi['highest_risk_score']),
         f"<b>{kpi['highest_risk_country']}</b> has highest risk score "
         f"({kpi['highest_risk_score']}%)"),
        ("🛫", "Commercial Jets account for highest incident category"),
        ("📅", "2020 saw a spike in Damage Severity Index"),
        ("⚠️", f"Weighted high-risk probability: "
               f"<b>{kpi['avg_high_risk_prob_weighted']}%</b>"),
        ("📊", f"Avg fatalities per fatal accident: "
               f"<b>{kpi['avg_fat_per_fatal']}</b>"),
    ]
    for icon, text in insights:
        st.markdown(
            f"<div class='insight-card'>{icon} {text}</div>",
            unsafe_allow_html=True
        )

st.divider()

# ═══════════════════════════════════════════════
#  ROW 4 — CHARTS GRID
# ═══════════════════════════════════════════════
st.markdown("""
    <div style='letter-spacing:2px; text-transform:uppercase; color:#00a8ff;
                font-family:"Share Tech Mono",monospace; font-size:1.1rem;
                border-bottom:1px solid rgba(0,168,255,0.2); padding-bottom:6px; margin-bottom:10px;'>
        // OVERVIEW CHARTS
    </div>
""", unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    st.plotly_chart(yoy_bar_chart(yearly), use_container_width=True)
with col_b:
    st.plotly_chart(fatality_severity_donut(df), use_container_width=True)

col_c, col_d = st.columns(2)
with col_c:
    st.plotly_chart(aircraft_bar_chart(df), use_container_width=True)
with col_d:
    st.plotly_chart(top_countries_chart(df), use_container_width=True)

st.plotly_chart(monthly_heatmap(df), use_container_width=True)

st.divider()

# ═══════════════════════════════════════════════
#  ROW 5 — NAVIGATION CARDS
# ═══════════════════════════════════════════════
st.markdown("""
    <div style='letter-spacing:2px; text-transform:uppercase; color:#00a8ff;
                font-family:"Share Tech Mono",monospace; font-size:1.1rem;
                border-bottom:1px solid rgba(0,168,255,0.2); padding-bottom:6px; margin-bottom:10px;'>
        // EXPLORE THE PLATFORM
    </div>
""", unsafe_allow_html=True)

pages = [
    ("📊", "Dashboard",        "Recreated interactive dashboard with all Power BI visuals",   "pages/2_Dashboard.py"),
    ("🤖", "AI Risk Predictor", "ML-powered accident risk prediction for any route/aircraft",  "pages/4_Risk_Predictor.py"),
    ("📈", "Trend Forecast",    "2026–2027 accident predictions using time series models",     "pages/5_Trend_Forecast.py"),
    ("📤", "Dynamic Analysis",  "Upload your own data and generate instant insights",          "pages/8_Dynamic_Analysis.py"),
]

cols = st.columns(4)
for col, (icon, title, desc, page) in zip(cols, pages):
    with col:
        st.markdown(f"""
            <div class='nav-card hud-panel'
                 style='background:linear-gradient(135deg, #0a0f14, #0d1128);
                        border:1px solid rgba(0,168,255,0.2); border-radius:8px;
                        padding:20px; text-align:center;'>
                <div class='nav-card-icon' style='font-size:2rem; margin-bottom:8px;'>{icon}</div>
                <div class='nav-card-title' style='color:#00a8ff; font-family:"Share Tech Mono",monospace;
                            font-size:1rem; font-weight:bold; margin-bottom:6px;
                            letter-spacing:1px;'>{title}</div>
                <div class='nav-card-desc' style='color:#7a8a9a; font-size:0.82rem;
                            margin-bottom:14px; line-height:1.4;'>{desc}</div>
                <a class='nav-card-btn' href='{page}'
                   style='display:inline-block; padding:6px 18px; border-radius:4px;
                          background:linear-gradient(135deg, rgba(0,168,255,0.15), rgba(0,212,255,0.1));
                          color:#00a8ff; text-decoration:none; font-size:0.85rem;
                          border:1px solid rgba(0,168,255,0.3);
                          font-family:"Share Tech Mono",monospace; letter-spacing:1px;
                          transition: all 0.3s ease;'>
                    OPEN {title.upper()}
                </a>
            </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════
st.markdown("""
    <div class='footer' style='text-align:center; color:#7a8a9a; font-size:0.8rem;
                padding:20px 0; margin-top:30px;
                border-top:1px solid rgba(0,168,255,0.2);
                font-family:"Share Tech Mono",monospace; letter-spacing:1px;'>
        <span style='color:#00a8ff;'>[</span> DATASET: Global Aviation Accidents 2015-2025 <span style='color:#00a8ff;'>]</span>
        &nbsp;|&nbsp;
        <span style='color:#00a8ff;'>[</span> THIRD YEAR DATA SCIENCE PROJECT <span style='color:#00a8ff;'>]</span>
        &nbsp;|&nbsp;
        <span style='color:#00a8ff;'>[</span> DOMAIN: Data Science <span style='color:#00a8ff;'>]</span>
        &nbsp;|&nbsp;
        <span style='color:#00a8ff;'>[</span> BUILT WITH STREAMLIT + PYTHON <span style='color:#00a8ff;'>]</span>
    </div>
""", unsafe_allow_html=True)
