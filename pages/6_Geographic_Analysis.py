import streamlit as st
import pandas as pd
import numpy as np
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_loader import load_main, load_risk_weighted, load_crash_risk, load_high_risk_prob
from utils.helpers import format_number, risk_emoji

st.set_page_config(page_title="Geographic Analysis | Aviation Safety",
                   page_icon="🗺️", layout="wide")

def load_css():
    css_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "style.css"))
    if os.path.exists(css_path):
         with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

# ── Load Data ────────────────────────────────────
df      = load_main()
risk_w  = load_risk_weighted()
crash_r = load_crash_risk()
high_r  = load_high_risk_prob()

# Merge all country tables
country_df = risk_w.merge(crash_r, on="country_clean", how="left")
country_df = country_df.merge(
    high_r[["country_clean","high_risk_probability","avg_fatal_probability","total_accidents"]],
    on="country_clean", how="left", suffixes=("","_hr")
)
# Add accident count from main table
acc_count = df.groupby("country_clean").size().reset_index(name="accident_count")
country_df = country_df.merge(acc_count, on="country_clean", how="left")
country_df["accident_count"] = country_df["accident_count"].fillna(0)

# ── Sidebar ──────────────────────────────────────
with st.sidebar:
    st.markdown("<h3 style='color:#4da6ff;'>✈️ Aviation Safety</h3>", unsafe_allow_html=True)
    st.divider()
    st.markdown("**🗺️ Map Settings**")
    map_metric = st.selectbox("Color Map By", [
        "overall_risk_score",
        "accident_count",
        "avg_fatal_risk",
        "avg_annual_crashes",
        "high_risk_probability"
    ], format_func=lambda x: {
        "overall_risk_score":    "Overall Risk Score",
        "accident_count":        "Total Accidents",
        "avg_fatal_risk":        "Avg Fatal Risk",
        "avg_annual_crashes":    "Avg Annual Crashes",
        "high_risk_probability": "High Risk Probability"
    }[x])

    top_n = st.slider("Top N Countries to Show", 5, 20, 10)
    st.divider()
    st.markdown("**🔍 Country Lookup**")
    lookup_country = st.selectbox(
        "Select Country for Details",
        options=sorted(country_df["country_clean"].unique().tolist()),
        index=sorted(country_df["country_clean"].unique().tolist()).index("United States")
    )

import plotly.express as px
import plotly.graph_objects as go

DARK = dict(plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
            font=dict(color="#ffffff"),
            margin=dict(l=10,r=10,t=40,b=10))

METRIC_LABELS = {
    "overall_risk_score":    "Overall Risk Score",
    "accident_count":        "Total Accidents",
    "avg_fatal_risk":        "Avg Fatal Risk",
    "avg_annual_crashes":    "Avg Annual Crashes",
    "high_risk_probability": "High Risk Probability"
}

# ═══════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════
st.markdown("<h1 style='color:#4da6ff;'>🗺️ Geographic Risk Analysis</h1>", unsafe_allow_html=True)
st.markdown("""
    <p style='color:#8899aa;'>
        Interactive world map showing aviation accident risk by country.
        Click sidebar to change metric, select country for detailed breakdown.
    </p>
""", unsafe_allow_html=True)
st.divider()

# ═══════════════════════════════════════════════
#  GLOBAL KPIs
# ═══════════════════════════════════════════════
g1, g2, g3, g4 = st.columns(4)
with g1:
    st.metric("🌍 Countries Covered", format_number(len(country_df)))
with g2:
    highest = country_df.loc[country_df["overall_risk_score"].idxmax(), "country_clean"]
    st.metric("⚠️ Highest Risk", highest)
with g3:
    safest_df = country_df[country_df["accident_count"] >= 5]
    safest = safest_df.loc[safest_df["overall_risk_score"].idxmin(), "country_clean"]
    st.metric("✅ Safest (5+ accidents)", safest)
with g4:
    avg_risk = round(country_df["overall_risk_score"].mean() * 100, 1)
    st.metric("📊 Global Avg Risk", f"{avg_risk}%")

st.divider()

# ═══════════════════════════════════════════════
#  WORLD MAP
# ═══════════════════════════════════════════════
st.subheader(f"🌍 World Map — {METRIC_LABELS[map_metric]}")

fig_map = px.choropleth(
    country_df,
    locations="country_clean",
    locationmode="country names",
    color=map_metric,
    color_continuous_scale=[[0,"#003366"],[0.4,"#0066cc"],[0.7,"#ffcc00"],[1,"#ff0044"]],
    hover_name="country_clean",
    hover_data={
        "overall_risk_score":    ":.3f",
        "accident_count":        ":.0f",
        "avg_fatal_risk":        ":.3f",
        "avg_annual_crashes":    ":.1f",
        "high_risk_probability": ":.3f"
    },
    labels={map_metric: METRIC_LABELS[map_metric]},
    title=f"Global Aviation {METRIC_LABELS[map_metric]} by Country"
)
fig_map.update_layout(
    paper_bgcolor="#0d1117",
    plot_bgcolor="#0d1117",
    font_color="#ffffff",
    geo=dict(
        bgcolor="#0a0e1a",
        lakecolor="#0a0e1a",
        landcolor="#1a2035",
        showframe=False,
        showcoastlines=True,
        coastlinecolor="#2a4a7f"
    ),
    margin=dict(l=0,r=0,t=40,b=0),
    height=480,
    coloraxis_colorbar=dict(
        tickfont=dict(color="#ffffff"),
        title=dict(text=METRIC_LABELS[map_metric], font=dict(color="#ffffff"))
    )
)
st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# ═══════════════════════════════════════════════
#  TOP N + BOTTOM N COUNTRIES
# ═══════════════════════════════════════════════
col_danger, col_safe = st.columns(2)

with col_danger:
    st.subheader(f"🔴 Top {top_n} Highest Risk Countries")
    top_df = country_df.nlargest(top_n, "overall_risk_score")[
        ["country_clean","overall_risk_score","accident_count","avg_fatal_risk"]
    ].reset_index(drop=True)
    top_df.index += 1
    top_df.columns = ["Country","Risk Score","Accidents","Fatal Risk"]
    top_df["Risk Score"] = (top_df["Risk Score"]*100).round(1).astype(str) + "%"
    top_df["Fatal Risk"] = (top_df["Fatal Risk"]*100).round(1).astype(str) + "%"
    top_df["Accidents"]  = top_df["Accidents"].astype(int)

    fig_top = px.bar(
        country_df.nlargest(top_n, "overall_risk_score").sort_values("overall_risk_score"),
        x="overall_risk_score", y="country_clean", orientation="h",
        color="overall_risk_score",
        color_continuous_scale=[[0,"#ffcc00"],[1,"#ff0044"]],
        labels={"overall_risk_score":"Risk Score","country_clean":"Country"}
    )
    fig_top.update_coloraxes(showscale=False)
    fig_top.update_layout(**DARK, height=380)
    st.plotly_chart(fig_top, use_container_width=True)
    st.dataframe(top_df, use_container_width=True)

with col_safe:
    st.subheader(f"🟢 Top {top_n} Safest Countries (5+ accidents)")
    safe_pool = country_df[country_df["accident_count"] >= 5]
    bot_df = safe_pool.nsmallest(top_n, "overall_risk_score")[
        ["country_clean","overall_risk_score","accident_count","avg_fatal_risk"]
    ].reset_index(drop=True)
    bot_df.index += 1
    bot_df.columns = ["Country","Risk Score","Accidents","Fatal Risk"]
    bot_df["Risk Score"] = (bot_df["Risk Score"]*100).round(1).astype(str) + "%"
    bot_df["Fatal Risk"] = (bot_df["Fatal Risk"]*100).round(1).astype(str) + "%"
    bot_df["Accidents"]  = bot_df["Accidents"].astype(int)

    fig_bot = px.bar(
        safe_pool.nsmallest(top_n, "overall_risk_score").sort_values("overall_risk_score", ascending=False),
        x="overall_risk_score", y="country_clean", orientation="h",
        color="overall_risk_score",
        color_continuous_scale=[[0,"#00ff88"],[1,"#ffcc00"]],
        labels={"overall_risk_score":"Risk Score","country_clean":"Country"}
    )
    fig_bot.update_coloraxes(showscale=False)
    fig_bot.update_layout(**DARK, height=380)
    st.plotly_chart(fig_bot, use_container_width=True)
    st.dataframe(bot_df, use_container_width=True)

st.divider()

# ═══════════════════════════════════════════════
#  COUNTRY DETAIL VIEW
# ═══════════════════════════════════════════════
st.subheader(f"🔍 Country Detail — {lookup_country}")

c_row       = country_df[country_df["country_clean"]==lookup_country]
c_accidents = df[df["country_clean"]==lookup_country]

if len(c_row) > 0:
    r         = c_row.iloc[0]
    risk_pct  = round(float(r["overall_risk_score"])*100, 1)
    risk_col  = "#ff0044" if risk_pct>60 else "#ff6600" if risk_pct>40 else "#ffcc00" if risk_pct>20 else "#00ff88"

    d1, d2 = st.columns([1, 2])

    with d1:
        st.markdown(f"""
            <div style='background:linear-gradient(135deg,#1a2035,#1e3a5f);
                        border-radius:14px;padding:24px;
                        border:2px solid {risk_col};'>
                <h3 style='color:#4da6ff;margin-top:0;'>{lookup_country}</h3>
                <div style='margin:16px 0;'>
                    <p style='color:#8899aa;margin:0;font-size:0.78rem;'>OVERALL RISK SCORE</p>
                    <div style='background:#0a0e1a;border-radius:8px;height:12px;margin:6px 0;'>
                        <div style='background:{risk_col};border-radius:8px;
                                    height:12px;width:{min(risk_pct,100)}%;'></div>
                    </div>
                    <p style='color:{risk_col};font-size:1.4rem;font-weight:700;margin:0;'>
                        {risk_emoji(risk_pct)} {risk_pct}%
                    </p>
                </div>
                <div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px;'>
                    <div><p style='color:#8899aa;margin:0;font-size:0.75rem;'>TOTAL ACCIDENTS</p>
                         <p style='color:#fff;margin:0;font-weight:600;font-size:1.1rem;'>{int(r.get("accident_count",0))}</p></div>
                    <div><p style='color:#8899aa;margin:0;font-size:0.75rem;'>AVG/YEAR</p>
                         <p style='color:#fff;margin:0;font-weight:600;font-size:1.1rem;'>{round(float(r.get("avg_annual_crashes",0)),1)}</p></div>
                    <div><p style='color:#8899aa;margin:0;font-size:0.75rem;'>FATAL RISK</p>
                         <p style='color:#ffcc00;margin:0;font-weight:600;font-size:1.1rem;'>{round(float(r.get("avg_fatal_risk",0))*100,1)}%</p></div>
                    <div><p style='color:#8899aa;margin:0;font-size:0.75rem;'>HIGH RISK PROB</p>
                         <p style='color:#ff6600;margin:0;font-weight:600;font-size:1.1rem;'>{round(float(r.get("high_risk_probability",0))*100,1)}%</p></div>
                    <div><p style='color:#8899aa;margin:0;font-size:0.75rem;'>SEVERE DAMAGE</p>
                         <p style='color:#fff;margin:0;font-weight:600;font-size:1.1rem;'>{round(float(r.get("severe_damage_rate",0))*100,1)}%</p></div>
                    <div><p style='color:#8899aa;margin:0;font-size:0.75rem;'>COUNTRY RANK</p>
                         <p style='color:#fff;margin:0;font-weight:600;font-size:1.1rem;'>
                             #{int(country_df["overall_risk_score"].rank(ascending=False)[c_row.index[0]])} / {len(country_df)}
                         </p></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with d2:
        if len(c_accidents) > 0:
            # Yearly trend for this country
            c_yearly = c_accidents.groupby("year").size().reset_index(name="accidents")
            fig_cy = go.Figure()
            fig_cy.add_trace(go.Bar(
                x=c_yearly["year"], y=c_yearly["accidents"],
                marker_color="#4da6ff",
                hovertemplate="<b>Year:</b> %{x}<br><b>Accidents:</b> %{y}<extra></extra>"
            ))
            fig_cy.update_layout(**DARK, height=220,
                                  title=f"Accidents Per Year — {lookup_country}",
                                  xaxis=dict(gridcolor="#1a2035", tickmode="linear", dtick=1),
                                  yaxis=dict(gridcolor="#1a2035"))
            st.plotly_chart(fig_cy, use_container_width=True)

            # Cause breakdown
            c_causes = c_accidents["reason_clean"].value_counts().reset_index()
            c_causes.columns = ["Cause","Count"]
            fig_cc = px.bar(c_causes.head(6), x="Count", y="Cause", orientation="h",
                            title=f"Top Causes — {lookup_country}")
            fig_cc.update_traces(marker_color="#ffcc00")
            fig_cc.update_layout(**DARK, height=220)
            st.plotly_chart(fig_cc, use_container_width=True)
        else:
            st.info(f"No accident records found for {lookup_country} in the main dataset.")

st.divider()

# ═══════════════════════════════════════════════
#  COUNTRY COMPARISON TOOL
# ═══════════════════════════════════════════════
st.subheader("⚖️ Compare Two Countries Side by Side")

all_countries = sorted(country_df["country_clean"].unique().tolist())
cmp1, cmp2 = st.columns(2)
with cmp1:
    country_a = st.selectbox("Country A", all_countries,
                              index=all_countries.index("United States"), key="cmp_a")
with cmp2:
    country_b = st.selectbox("Country B", all_countries,
                              index=all_countries.index("Dominican Republic"), key="cmp_b")

if st.button("⚡ Compare Countries", use_container_width=True):
    metrics = {
        "Overall Risk Score":    ("overall_risk_score",    True,  "%",    100),
        "Total Accidents":       ("accident_count",        True,  "",     1),
        "Avg Annual Crashes":    ("avg_annual_crashes",    True,  "",     1),
        "Avg Fatal Risk":        ("avg_fatal_risk",        True,  "%",    100),
        "High Risk Probability": ("high_risk_probability", True,  "%",    100),
        "Severe Damage Rate":    ("severe_damage_rate",    True,  "%",    100),
    }

    row_a = country_df[country_df["country_clean"]==country_a].iloc[0]
    row_b = country_df[country_df["country_clean"]==country_b].iloc[0]

    # Radar chart
    radar_metrics = ["overall_risk_score","avg_fatal_risk",
                     "high_risk_probability","severe_damage_rate"]
    radar_labels  = ["Overall Risk","Fatal Risk","High Risk Prob","Severe Damage"]

    vals_a = [float(row_a.get(m,0)) for m in radar_metrics]
    vals_b = [float(row_b.get(m,0)) for m in radar_metrics]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=vals_a + [vals_a[0]], theta=radar_labels + [radar_labels[0]],
        fill="toself", name=country_a,
        line=dict(color="#4da6ff"), fillcolor="rgba(77,166,255,0.15)"
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=vals_b + [vals_b[0]], theta=radar_labels + [radar_labels[0]],
        fill="toself", name=country_b,
        line=dict(color="#ff0044"), fillcolor="rgba(255,0,68,0.15)"
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="#0d1117",
            radialaxis=dict(visible=True, range=[0,1], gridcolor="#1a2035", color="#8899aa"),
            angularaxis=dict(gridcolor="#1a2035", color="#8899aa")
        ),
        paper_bgcolor="#0d1117",
        font=dict(color="#ffffff"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#ffffff")),
        height=380
    )

    radar_col, table_col = st.columns([1,1])
    with radar_col:
        st.plotly_chart(fig_radar, use_container_width=True)
    with table_col:
        cmp_rows = []
        for label, (col, higher_worse, suffix, mult) in metrics.items():
            val_a = float(row_a.get(col,0)) * mult
            val_b = float(row_b.get(col,0)) * mult
            if higher_worse:
                winner = country_a if val_a < val_b else country_b
            else:
                winner = country_a if val_a > val_b else country_b
            cmp_rows.append({
                "Metric": label,
                country_a: f"{val_a:.1f}{suffix}",
                country_b: f"{val_b:.1f}{suffix}",
                "Safer": f"✅ {winner}"
            })
        cmp_df = pd.DataFrame(cmp_rows)
        st.dataframe(cmp_df, use_container_width=True, hide_index=True, height=280)

        # Overall verdict
        risk_a = float(row_a.get("overall_risk_score",0))
        risk_b = float(row_b.get("overall_risk_score",0))
        safer  = country_a if risk_a < risk_b else country_b
        diff   = abs(risk_a - risk_b) * 100
        st.markdown(f"""
            <div style='background:#1a2035;border-radius:10px;padding:16px;
                        border:1px solid #00ff88;text-align:center;margin-top:12px;'>
                <p style='color:#8899aa;margin:0;font-size:0.85rem;'>OVERALL VERDICT</p>
                <h3 style='color:#00ff88;margin:6px 0;'>✅ {safer} is safer</h3>
                <p style='color:#c9d1d9;margin:0;font-size:0.9rem;'>
                    by {diff:.1f}% overall risk score
                </p>
            </div>
        """, unsafe_allow_html=True)

st.divider()
st.markdown("<div class='footer'>🗺️ Geographic Analysis | Aviation Safety Intelligence Platform</div>",
            unsafe_allow_html=True)
