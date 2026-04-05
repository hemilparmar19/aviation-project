import streamlit as st
import pandas as pd
import os, sys, io
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_loader import (load_main, load_risk_weighted, load_crash_risk,
                                load_high_risk_prob, get_kpi_metrics, get_yearly_trend,
                                get_cause_contribution)
from utils.helpers import format_number, format_pct

st.set_page_config(page_title="Report Generator | Aviation Safety",
                   page_icon="📄", layout="wide")

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
kpi     = get_kpi_metrics(df, risk_w, high_r)
yearly  = get_yearly_trend(df)
causes  = get_cause_contribution(df)

# ── Sidebar ──────────────────────────────────────
with st.sidebar:
    st.markdown("<h3 style='color:#4da6ff;'>✈️ Aviation Safety</h3>", unsafe_allow_html=True)
    st.divider()
    st.markdown("**📄 Report Settings**")
    report_title = st.text_input("Report Title", value="Global Aviation Accident Analysis Report")
    author_name  = st.text_input("Author / Team Name", value="Hitanshi Parekh & Sakshi Darji")
    year_range   = st.slider("Year Range", 2015, 2025, (2015, 2025))
    st.divider()
    st.markdown("**📋 Include Sections**")
    inc_summary  = st.checkbox("Executive Summary",     value=True)
    inc_stats    = st.checkbox("Key Statistics",         value=True)
    inc_trend    = st.checkbox("Trend Analysis",         value=True)
    inc_risk     = st.checkbox("Risk Analysis",          value=True)
    inc_causes   = st.checkbox("Cause Analysis",         value=True)
    inc_aircraft = st.checkbox("Aircraft Category",      value=True)
    inc_rec      = st.checkbox("Recommendations",        value=True)

# ── Filter data by year range ────────────────────
df_filtered = df[df["year"].between(year_range[0], year_range[1])]
kpi_f = get_kpi_metrics(df_filtered, risk_w, high_r)
yearly_f = get_yearly_trend(df_filtered)
causes_f = get_cause_contribution(df_filtered)

# ═══════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════
st.markdown("<h1 style='color:#4da6ff;'>📄 Report Generator</h1>", unsafe_allow_html=True)
st.markdown("""
    <p style='color:#8899aa;'>
        Configure your report in the sidebar, preview it below,
        then download as CSV data or formatted text report.
    </p>
""", unsafe_allow_html=True)
st.divider()

# ═══════════════════════════════════════════════
#  LIVE REPORT PREVIEW
# ═══════════════════════════════════════════════
st.markdown(f"""
    <div style='background:linear-gradient(135deg,#1a2035,#0d1117);
                border-radius:14px;padding:32px;border:1px solid #2a4a7f;'>
        <div style='text-align:center;border-bottom:2px solid #4da6ff;padding-bottom:20px;margin-bottom:24px;'>
            <h1 style='color:#4da6ff;margin:0;font-size:1.8rem;'>✈️ {report_title}</h1>
            <p style='color:#8899aa;margin:8px 0 0 0;'>
                Period: {year_range[0]} – {year_range[1]} &nbsp;|&nbsp;
                Generated: {datetime.now().strftime("%B %d, %Y")} &nbsp;|&nbsp;
                By: {author_name}
            </p>
        </div>
""", unsafe_allow_html=True)

# ── Executive Summary ────────────────────────────
if inc_summary:
    trend_word = "decline" if yearly_f["total_accidents"].iloc[-1] < yearly_f["total_accidents"].iloc[0] else "increase"
    st.markdown(f"""
        <div style='margin-bottom:24px;'>
            <h2 style='color:#4da6ff;'>1. Executive Summary</h2>
            <p style='color:#c9d1d9;line-height:1.8;'>
                This report presents a comprehensive analysis of global aviation accidents
                from <b>{year_range[0]}</b> to <b>{year_range[1]}</b>.
                During this period, a total of <b>{format_number(kpi_f["total_accidents"])} accidents</b>
                were recorded worldwide, resulting in
                <b>{format_number(kpi_f["total_fatalities"])} fatalities</b>.
                The fatal accident rate stands at <b>{format_pct(kpi_f["fatal_accident_pct"])}</b>,
                with the <b>{kpi_f["highest_risk_country"]}</b> identified as the highest-risk country.
                Overall, accident figures show a <b>{trend_word}</b> over the analysis period,
                with <b>Runway Excursion</b> remaining the leading cause of incidents globally.
            </p>
        </div>
    """, unsafe_allow_html=True)

# ── Key Statistics ───────────────────────────────
if inc_stats:
    st.markdown("<h2 style='color:#4da6ff;'>2. Key Statistics</h2>", unsafe_allow_html=True)
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    with r1c1: st.metric("Total Accidents",     format_number(kpi_f["total_accidents"]))
    with r1c2: st.metric("Total Fatalities",    format_number(kpi_f["total_fatalities"]))
    with r1c3: st.metric("Fatal Accident %",    format_pct(kpi_f["fatal_accident_pct"]))
    with r1c4: st.metric("Damage Severity Idx", f"{kpi_f['damage_severity_index']:.3f}")
    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1: st.metric("Fatal Accidents",       format_number(kpi_f["fatal_accidents"]))
    with r2c2: st.metric("Non-Fatal Accidents",   format_number(kpi_f["non_fatal_accidents"]))
    with r2c3: st.metric("Commercial Accidents",  format_number(kpi_f["commercial_accidents"]))
    with r2c4: st.metric("High Severity Events",  format_number(kpi_f["high_severity_accidents"]))
    st.markdown("<br>", unsafe_allow_html=True)

# ── Trend Analysis ───────────────────────────────
if inc_trend:
    import plotly.graph_objects as go
    st.markdown("<h2 style='color:#4da6ff;'>3. Trend Analysis</h2>", unsafe_allow_html=True)
    tc1, tc2 = st.columns(2)
    with tc1:
        fig_t = go.Figure()
        fig_t.add_trace(go.Scatter(
            x=yearly_f["year"], y=yearly_f["total_accidents"],
            mode="lines+markers", line=dict(color="#4da6ff", width=3),
            marker=dict(size=8), fill="tozeroy", fillcolor="rgba(77,166,255,0.1)"
        ))
        fig_t.update_layout(
            title="Accident Trend",
            plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
            font=dict(color="#ffffff"), height=280,
            margin=dict(l=10,r=10,t=40,b=10),
            xaxis=dict(gridcolor="#1a2035",tickmode="linear",dtick=1),
            yaxis=dict(gridcolor="#1a2035")
        )
        st.plotly_chart(fig_t, use_container_width=True)
    with tc2:
        fig_d = go.Figure()
        fig_d.add_trace(go.Scatter(
            x=yearly_f["year"], y=yearly_f["avg_damage_severity"],
            mode="lines+markers", line=dict(color="#ffcc00", width=3),
            marker=dict(size=8), fill="tozeroy", fillcolor="rgba(255,204,0,0.1)"
        ))
        fig_d.update_layout(
            title="Damage Severity Index Trend",
            plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
            font=dict(color="#ffffff"), height=280,
            margin=dict(l=10,r=10,t=40,b=10),
            xaxis=dict(gridcolor="#1a2035",tickmode="linear",dtick=1),
            yaxis=dict(gridcolor="#1a2035")
        )
        st.plotly_chart(fig_d, use_container_width=True)

# ── Risk Analysis ────────────────────────────────
if inc_risk:
    import plotly.express as px
    st.markdown("<h2 style='color:#4da6ff;'>4. Risk Analysis</h2>", unsafe_allow_html=True)
    risk_top = risk_w.nlargest(10, "overall_risk_score")
    fig_r = px.bar(
        risk_top.sort_values("overall_risk_score"),
        x="overall_risk_score", y="country_clean", orientation="h",
        color="overall_risk_score",
        color_continuous_scale=[[0,"#ffcc00"],[1,"#ff0044"]],
        labels={"overall_risk_score":"Overall Risk Score","country_clean":"Country"},
        title="Top 10 Highest Risk Countries"
    )
    fig_r.update_coloraxes(showscale=False)
    fig_r.update_layout(
        plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
        font=dict(color="#ffffff"), height=320,
        margin=dict(l=10,r=10,t=40,b=10),
        xaxis=dict(gridcolor="#1a2035"), yaxis=dict(gridcolor="#1a2035")
    )
    st.plotly_chart(fig_r, use_container_width=True)

# ── Cause Analysis ───────────────────────────────
if inc_causes:
    st.markdown("<h2 style='color:#4da6ff;'>5. Cause Analysis</h2>", unsafe_allow_html=True)
    import plotly.express as px
    fig_c = px.bar(
        causes_f.head(12).sort_values("total_accidents"),
        x="total_accidents", y="reason_clean", orientation="h",
        color="cause_contribution_pct",
        color_continuous_scale=[[0,"#1a3a6f"],[1,"#4da6ff"]],
        labels={"total_accidents":"Total Accidents","reason_clean":"Cause","cause_contribution_pct":"Contribution %"},
        title="Primary Causes of Aviation Accidents"
    )
    fig_c.update_coloraxes(showscale=False)
    fig_c.update_layout(
        plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
        font=dict(color="#ffffff"), height=380,
        margin=dict(l=10,r=10,t=40,b=10),
        xaxis=dict(gridcolor="#1a2035"), yaxis=dict(gridcolor="#1a2035")
    )
    st.plotly_chart(fig_c, use_container_width=True)

# ── Aircraft Category ────────────────────────────
if inc_aircraft:
    st.markdown("<h2 style='color:#4da6ff;'>6. Aircraft Category Analysis</h2>", unsafe_allow_html=True)
    ac_df = df_filtered["aircraft_category"].value_counts().reset_index()
    ac_df.columns = ["Category","Count"]
    ac1, ac2 = st.columns(2)
    with ac1:
        import plotly.express as px
        fig_ac = px.pie(ac_df, values="Count", names="Category",
                        hole=0.45, title="Accidents by Aircraft Category")
        fig_ac.update_layout(
            plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
            font=dict(color="#ffffff"), height=300, margin=dict(l=10,r=10,t=40,b=10),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#ffffff"))
        )
        st.plotly_chart(fig_ac, use_container_width=True)
    with ac2:
        sev_ac = df_filtered.groupby(["aircraft_category","Fatality_Severity"]).size().reset_index(name="count")
        fig_sv = px.bar(sev_ac, x="aircraft_category", y="count", color="Fatality_Severity",
                        barmode="stack",
                        color_discrete_map={"Non-Fatal":"#00ff88","Low":"#ffcc00",
                                             "Medium":"#ff6600","High":"#ff0044"},
                        title="Severity by Aircraft Category")
        fig_sv.update_layout(
            plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
            font=dict(color="#ffffff"), height=300,
            margin=dict(l=10,r=10,t=40,b=10),
            xaxis=dict(gridcolor="#1a2035",tickangle=-30),
            yaxis=dict(gridcolor="#1a2035"),
            legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#ffffff"))
        )
        st.plotly_chart(fig_sv, use_container_width=True)

# ── Recommendations ──────────────────────────────
if inc_rec:
    st.markdown("<h2 style='color:#4da6ff;'>7. Recommendations</h2>", unsafe_allow_html=True)
    top_cause = causes_f.iloc[0]["reason_clean"]
    recs = [
        ("🛬", "Runway Safety",        f"Implement advanced runway safety systems to address <b>{top_cause}</b>, the leading cause of accidents ({causes_f.iloc[0]['cause_contribution_pct']}% of all incidents)."),
        ("🌍", "High-Risk Countries",  f"Prioritize aviation safety audits in <b>{kpi_f['highest_risk_country']}</b> and other high-risk nations identified in the risk assessment."),
        ("🔧", "Aircraft Maintenance", "Strengthen engine technical failure prevention through enhanced maintenance protocols, particularly for Commercial Jet and Private General Aviation categories."),
        ("🌦️", "Weather Protocols",    "Improve turbulence and weather-related safety procedures, especially for routes in historically high-incident regions."),
        ("📚", "Pilot Training",       "Expand human factor and training procedure programs to reduce stall/loss of control incidents, the second leading cause of accidents."),
        ("📊", "Data Collection",      "Standardize accident reporting across all countries to improve data quality and enable more accurate risk assessment."),
    ]
    for icon, title, text in recs:
        st.markdown(f"""
            <div style='background:#0d1117;border-radius:10px;padding:14px 18px;
                        margin:8px 0;border-left:3px solid #4da6ff;'>
                <b style='color:#4da6ff;'>{icon} {title}:</b>
                <span style='color:#c9d1d9;'> {text}</span>
            </div>
        """, unsafe_allow_html=True)

# Close the report card
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ═══════════════════════════════════════════════
#  DOWNLOAD OPTIONS
# ═══════════════════════════════════════════════
st.subheader("⬇️ Download Report")
dl1, dl2, dl3 = st.columns(3)

# ── CSV Data Export ──────────────────────────────
with dl1:
    st.markdown("""
        <div style='background:#1a2035;border-radius:10px;padding:16px;
                    border:1px solid #2a4a7f;text-align:center;margin-bottom:12px;'>
            <div style='font-size:2rem;'>📊</div>
            <h4 style='color:#4da6ff;margin:8px 0 4px;'>Full Dataset (CSV)</h4>
            <p style='color:#8899aa;font-size:0.82rem;margin:0;'>All accident records for selected period</p>
        </div>
    """, unsafe_allow_html=True)
    st.download_button(
        "⬇️ Download Accident Data",
        data=df_filtered.to_csv(index=False),
        file_name=f"aviation_accidents_{year_range[0]}_{year_range[1]}.csv",
        mime="text/csv",
        use_container_width=True
    )

# ── Statistics Export ────────────────────────────
with dl2:
    st.markdown("""
        <div style='background:#1a2035;border-radius:10px;padding:16px;
                    border:1px solid #2a4a7f;text-align:center;margin-bottom:12px;'>
            <div style='font-size:2rem;'>📈</div>
            <h4 style='color:#4da6ff;margin:8px 0 4px;'>Statistics (CSV)</h4>
            <p style='color:#8899aa;font-size:0.82rem;margin:0;'>Yearly trends and KPI metrics</p>
        </div>
    """, unsafe_allow_html=True)
    stats_df = pd.DataFrame([{
        "Metric": k.replace("_"," ").title(), "Value": str(v)
    } for k,v in kpi_f.items()])
    st.download_button(
        "⬇️ Download Statistics",
        data=yearly_f.to_csv(index=False),
        file_name=f"aviation_statistics_{year_range[0]}_{year_range[1]}.csv",
        mime="text/csv",
        use_container_width=True
    )

# ── Text Report ──────────────────────────────────
with dl3:
    st.markdown("""
        <div style='background:#1a2035;border-radius:10px;padding:16px;
                    border:1px solid #2a4a7f;text-align:center;margin-bottom:12px;'>
            <div style='font-size:2rem;'>📝</div>
            <h4 style='color:#4da6ff;margin:8px 0 4px;'>Text Report (.txt)</h4>
            <p style='color:#8899aa;font-size:0.82rem;margin:0;'>Formatted summary report</p>
        </div>
    """, unsafe_allow_html=True)

    report_text = f"""
{'='*60}
{report_title.upper()}
{'='*60}
Period    : {year_range[0]} - {year_range[1]}
Generated : {datetime.now().strftime("%B %d, %Y at %H:%M")}
Author    : {author_name}
{'='*60}

EXECUTIVE SUMMARY
-----------------
Total Accidents   : {format_number(kpi_f['total_accidents'])}
Total Fatalities  : {format_number(kpi_f['total_fatalities'])}
Fatal Accident %  : {format_pct(kpi_f['fatal_accident_pct'])}
Damage Sev. Index : {kpi_f['damage_severity_index']:.3f}
Highest Risk      : {kpi_f['highest_risk_country']}
YOY Change        : {kpi_f['yoy_pct']:+.2f}%

YEARLY BREAKDOWN
----------------
"""
    for _, row in yearly_f.iterrows():
        yoy = f"{row['yoy_change_pct']:+.1f}%" if pd.notna(row["yoy_change_pct"]) else "  N/A "
        report_text += f"  {int(row['year'])} | Accidents: {int(row['total_accidents']):>4} | Fatalities: {int(row['total_fatalities']):>5} | YOY: {yoy}\n"

    report_text += f"""
TOP 5 ACCIDENT CAUSES
---------------------
"""
    for _, row in causes_f.head(5).iterrows():
        report_text += f"  {row['reason_clean']:<35} {int(row['total_accidents']):>4} accidents ({row['cause_contribution_pct']:.1f}%)\n"

    report_text += f"""
TOP 5 HIGHEST RISK COUNTRIES
-----------------------------
"""
    for i, (_, row) in enumerate(risk_w.nlargest(5,"overall_risk_score").iterrows(), 1):
        report_text += f"  {i}. {row['country_clean']:<25} Risk: {row['overall_risk_score']*100:.1f}%\n"

    report_text += f"""
RECOMMENDATIONS
---------------
1. Address Runway Excursion as top priority safety initiative
2. Focus safety audits on highest-risk countries
3. Strengthen engine maintenance protocols
4. Improve weather-related safety procedures
5. Expand pilot training programs
6. Standardize global accident reporting

{'='*60}
Report generated by Aviation Safety Intelligence Platform
Third Year Data Science Project | {datetime.now().year}
{'='*60}
"""
    st.download_button(
        "⬇️ Download Text Report",
        data=report_text,
        file_name=f"aviation_report_{year_range[0]}_{year_range[1]}.txt",
        mime="text/plain",
        use_container_width=True
    )

# ── Risk Country CSV ─────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col_r1, col_r2, _ = st.columns([1,1,2])
with col_r1:
    st.download_button(
        "⬇️ Country Risk Data (CSV)",
        data=risk_w.to_csv(index=False),
        file_name="country_risk_analysis.csv",
        mime="text/csv",
        use_container_width=True
    )
with col_r2:
    st.download_button(
        "⬇️ Cause Analysis (CSV)",
        data=causes_f.to_csv(index=False),
        file_name="cause_analysis.csv",
        mime="text/csv",
        use_container_width=True
    )

st.divider()
st.markdown("<div class='footer'>📄 Report Generator | Aviation Safety Intelligence Platform</div>",
            unsafe_allow_html=True)
