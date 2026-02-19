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
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

# ── Sidebar ─────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding:10px 0 20px 0;'>
            <h2 style='color:#4da6ff; margin:0;'>✈️</h2>
            <h3 style='color:#4da6ff; margin:4px 0 0 0;'>Aviation Safety</h3>
            <p style='color:#8899aa; font-size:0.8rem; margin:0;'>Intelligence Platform</p>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("""
        <div style='color:#8899aa; font-size:0.8rem; line-height:2;'>
            📊 <b style='color:#c9d1d9;'>Dataset:</b> 2015–2025<br>
            🌍 <b style='color:#c9d1d9;'>Coverage:</b> Global<br>
            📁 <b style='color:#c9d1d9;'>Records:</b> 2,596 accidents<br>
            🗂️ <b style='color:#c9d1d9;'>Tables:</b> 4 (joined)<br>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("""
        <div style='color:#8899aa; font-size:0.78rem; text-align:center;'>
            🎓 Third Year Data Science Project<br>
            <b style='color:#c9d1d9;'>Trend Analysis of Global<br>Airplane Accidents</b>
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
    <div style='text-align:center; padding:30px 0 10px 0;'>
        <h1 style='font-size:2.8rem; color:#4da6ff; margin-bottom:8px;'>
            ✈️ Global Aviation Accident Analysis
        </h1>
        <p style='font-size:1.1rem; color:#8899aa; max-width:700px; margin:0 auto;'>
            A comprehensive trend analysis of worldwide aviation accidents
            from <b style='color:#c9d1d9;'>2015</b> to <b style='color:#c9d1d9;'>2025</b>,
            powered by machine learning and data science.
        </p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# ═══════════════════════════════════════════════
#  ROW 1 — KPI METRICS (matching Power BI exactly)
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
    st.subheader("📈 Global Accident Trend")
    st.plotly_chart(trend_line_chart(yearly),
                    use_container_width=True)

with insight_col:
    st.subheader("💡 Key Insights")
    insights = [
        ("📉", "Accidents declined significantly from the 2019 peak to 2024"),
        ("✈️", f"Most common cause: <b>Runway Excursion</b>"),
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
st.subheader("📊 Overview Charts")

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
st.subheader("🚀 Explore the Platform")

n1, n2, n3 = st.columns(3)

pages = [
    ("📊", "Dashboard",      "Recreated interactive dashboard with all Power BI visuals",   "pages/2_Dashboard.py"),
    ("🤖", "AI Risk Predictor","ML-powered accident risk prediction for any route/aircraft", "pages/4_Risk_Predictor.py"),
    ("📈", "Trend Forecast",  "2026–2027 accident predictions using time series models",     "pages/5_Trend_Forecast.py"),
]

for col, (icon, title, desc, page) in zip([n1, n2, n3], pages):
    with col:
        st.markdown(f"""
            <div class='nav-card'>
                <div style='font-size:2rem;'>{icon}</div>
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
        """, unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button(f"Open {title}", key=f"nav_{title}"):
                st.switch_page(page)

# ═══════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════
st.markdown("""
    <div class='footer'>
        📁 Dataset: Global Aviation Accidents 2015–2025 &nbsp;|&nbsp;
        🎓 Third Year Data Science Project &nbsp;|&nbsp;
        Domain: Data Science &nbsp;|&nbsp;
        👥 Built with Streamlit + Python
    </div>
""", unsafe_allow_html=True)
