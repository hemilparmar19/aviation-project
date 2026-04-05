import streamlit as st
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_loader import (load_main, load_risk_weighted,
                                load_high_risk_prob, load_crash_risk,
                                get_kpi_metrics, get_yearly_trend,
                                get_cause_contribution)
from utils.charts import (trend_line_chart, aircraft_bar_chart,
                          top_countries_chart, cause_contribution_chart,
                          damage_severity_trend, risk_scatter_chart,
                          top_risk_countries_chart)
from utils.helpers import format_number, format_pct

st.set_page_config(page_title="Dashboard | Aviation Safety",
                   page_icon="📊", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_path):
         with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

# Sidebar
with st.sidebar:
    st.markdown("<h3 style='color:#00a8ff; font-family:\"Share Tech Mono\",monospace; "
                "text-shadow:0 0 8px rgba(0,168,255,0.3);'>AVIATION SAFETY</h3>",
                unsafe_allow_html=True)
    st.divider()
    st.markdown("**🔽 Global Filters**")
    df_temp = load_main()
    year_range = st.slider("Year Range", 2015, 2025, (2015, 2025))
    aircraft_filter = st.multiselect(
        "Aircraft Category",
        options=["All"] + sorted(df_temp["aircraft_category"].unique().tolist()),
        default=["All"]
    )
    cause_filter = st.multiselect(
        "Accident Cause",
        options=["All"] + sorted(df_temp["reason_clean"].unique().tolist()),
        default=["All"]
    )

# ── Load & Filter Data ───────────────────────────
df        = load_main()
risk_w    = load_risk_weighted()
high_risk = load_high_risk_prob()
crash_r   = load_crash_risk()

# Apply sidebar filters
mask = df["year"].between(year_range[0], year_range[1])
if "All" not in aircraft_filter:
    mask &= df["aircraft_category"].isin(aircraft_filter)
if "All" not in cause_filter:
    mask &= df["reason_clean"].isin(cause_filter)
df_filtered = df[mask]

kpi    = get_kpi_metrics(df_filtered, risk_w, high_risk)
yearly = get_yearly_trend(df_filtered)
causes = get_cause_contribution(df_filtered)

# ═══════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════
st.markdown("""
    <h1 style='color:#00a8ff; text-shadow:0 0 15px rgba(0,168,255,0.3);'>📊 Interactive Dashboard</h1>
    <p style='color:#7a8a9a;'>
        Fully recreated from Power BI — all DAX measures recalculated in Python.
        Use sidebar filters to explore the data.
    </p>
""", unsafe_allow_html=True)
st.divider()

# ═══════════════════════════════════════════════
#  THREE DASHBOARD TABS (matching Power BI pages)
# ═══════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "📊 Page 1 — Overview & Trends",
    "⚠️  Page 2 — Risk Analysis",
    "🔥 Page 3 — High-Risk Accidents"
])

# ─────────────────────────────────────────────
#  TAB 1 — Overview & Trends (matches PBI page 1)
# ─────────────────────────────────────────────
with tab1:
    st.markdown("### Overview & Trends")

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Accidents", format_number(kpi["total_accidents"]))
    with k2:
        st.metric("Total Fatalities", format_number(kpi["total_fatalities"]))
    with k3:
        st.metric("Fatal Accident %", format_pct(kpi["fatal_accident_pct"]))
    with k4:
        st.metric("Accidents YOY %", format_pct(abs(kpi["yoy_pct"])))

    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.plotly_chart(trend_line_chart(yearly), use_container_width=True)
    with col_right:
        st.plotly_chart(top_countries_chart(df_filtered), use_container_width=True)

    st.plotly_chart(aircraft_bar_chart(df_filtered), use_container_width=True)


# ─────────────────────────────────────────────
#  TAB 2 — Risk Analysis (matches PBI page 2)
# ─────────────────────────────────────────────
with tab2:
    st.markdown("### Country Risk Analysis")

    r1, r2 = st.columns(2)
    with r1:
        st.metric("Highest Risk Country",
                  kpi["highest_risk_country"],
                  f"{kpi['highest_risk_score']}% overall risk",
                  delta_color="inverse")
    with r2:
        st.metric("Avg High Risk Probability (Weighted)",
                  format_pct(kpi["avg_high_risk_prob_weighted"]),
                  "Across all countries")

    st.divider()

    col_map, col_bar = st.columns(2)
    with col_map:
        # Choropleth world map
        import plotly.express as px
        fig_map = px.choropleth(
            risk_w,
            locations="country_clean",
            locationmode="country names",
            color="overall_risk_score",
            color_continuous_scale=[[0,"#001a33"],[0.5,"#ff9500"],[1,"#ff0044"]],
            hover_name="country_clean",
            hover_data={
                "overall_risk_score": ":.3f",
                "avg_fatal_risk":     ":.3f",
                "severe_damage_rate": ":.3f"
            },
            labels={"overall_risk_score": "Overall Risk Score"},
            title="Overall Aviation Risk by Country"
        )
        fig_map.update_layout(
            paper_bgcolor="#0a0f14",
            plot_bgcolor="#0a0f14",
            font_color="#e0e0e0",
            geo=dict(
                bgcolor="#060a0f",
                lakecolor="#060a0f",
                landcolor="#0a0f14",
                showframe=False,
                showcoastlines=True,
                coastlinecolor="rgba(0,168,255,0.2)"
            ),
            margin=dict(l=0,r=0,t=40,b=0),
            height=380,
            coloraxis_colorbar=dict(
                tickfont=dict(color="#e0e0e0"),
                title=dict(text="Risk Score", font=dict(color="#e0e0e0"))
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_bar:
        st.plotly_chart(top_risk_countries_chart(risk_w), use_container_width=True)

    col_scatter, col_damage = st.columns(2)
    with col_scatter:
        st.plotly_chart(risk_scatter_chart(risk_w), use_container_width=True)
    with col_damage:
        st.plotly_chart(damage_severity_trend(yearly), use_container_width=True)


# ─────────────────────────────────────────────
#  TAB 3 — High-Risk Accidents (matches PBI page 3)
# ─────────────────────────────────────────────
with tab3:
    st.markdown("### High-Risk Accident Deep Dive")

    h1, h2 = st.columns(2)
    with h1:
        st.metric("Fatal Accident Rate",
                  format_pct(kpi["fatal_accident_pct"]),
                  delta_color="inverse")
    with h2:
        st.metric("High Severity Accidents",
                  format_number(kpi["high_severity_accidents"]),
                  "Fatality_Severity = High",
                  delta_color="inverse")

    st.divider()

    col_cat, col_cause = st.columns(2)
    with col_cat:
        # High-risk accidents by aircraft category
        high_risk_df = df_filtered[df_filtered["Fatality_Severity"] == "High"]
        st.plotly_chart(aircraft_bar_chart(high_risk_df),
                        use_container_width=True)
        st.caption("High-Risk Accidents by Aircraft Category")

    with col_cause:
        st.plotly_chart(cause_contribution_chart(causes),
                        use_container_width=True)

    st.divider()

    # Data table (matches PBI page 3 table)
    st.markdown("### 📋 Accident Detail Table")
    display_cols = ["acc._date", "country_clean", "aircraft_category",
                    "reason_clean", "Fatality_Severity", "dmg_clean",
                    "fat.", "location"]
    available_cols = [c for c in display_cols if c in df_filtered.columns]

    st.dataframe(
        df_filtered[available_cols].rename(columns={
            "acc._date":        "Date",
            "country_clean":    "Country",
            "aircraft_category":"Aircraft Category",
            "reason_clean":     "Cause",
            "Fatality_Severity":"Severity",
            "dmg_clean":        "Damage",
            "fat.":             "Fatalities",
            "location":         "Location"
        }).sort_values("Date", ascending=False).reset_index(drop=True),
        use_container_width=True,
        height=400
    )

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv_data = df_filtered[available_cols].to_csv(index=False)
        st.download_button(
            "⬇️ Download Filtered Data (CSV)",
            data=csv_data,
            file_name=f"aviation_accidents_{year_range[0]}_{year_range[1]}.csv",
            mime="text/csv"
        )
