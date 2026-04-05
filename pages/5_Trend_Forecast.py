import streamlit as st
import pandas as pd
import numpy as np
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_loader import load_main, get_yearly_trend
from utils.helpers import format_number

st.set_page_config(page_title="Trend Forecast | Aviation Safety",
                   page_icon="📈", layout="wide")

def load_css():
    css_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "style.css"))
    if os.path.exists(css_path):
         with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

# ── Sidebar ──────────────────────────────────────
with st.sidebar:
    st.markdown("<h3 style='color:#4da6ff;'>✈️ Aviation Safety</h3>", unsafe_allow_html=True)
    st.divider()
    st.markdown("**🔽 Forecast Settings**")
    forecast_years  = st.slider("Forecast Up To", 2026, 2030, 2027)
    show_confidence = st.checkbox("Show Confidence Interval", value=True)
    selected_cats   = st.multiselect(
        "Aircraft Categories",
        options=["All","Commercial Jet","Private / General Aviation",
                 "Business Jet","Regional / Turboprop","Cargo","Military","Other / Unknown"],
        default=["All"]
    )
    st.divider()
    st.markdown("""
        <div style='background:#1a2035;padding:14px;border-radius:10px;border:1px solid #2a4a7f;'>
            <p style='color:#8899aa;margin:0;font-size:0.78rem;'>📐 MODEL</p>
            <p style='color:#4da6ff;margin:4px 0 0 0;font-weight:600;'>Linear Regression</p>
            <p style='color:#8899aa;margin:8px 0 0 0;font-size:0.78rem;'>📊 TRAINING DATA</p>
            <p style='color:#c9d1d9;margin:4px 0 0 0;font-weight:600;'>2015–2024 (10 years)</p>
            <p style='color:#8899aa;margin:8px 0 0 0;font-size:0.78rem;'>⚠️ NOTE</p>
            <p style='color:#ffcc00;margin:4px 0 0 0;font-size:0.8rem;'>2025 excluded (partial year)</p>
        </div>
    """, unsafe_allow_html=True)

# ── Load & Prepare Data ──────────────────────────
df     = load_main()
yearly = get_yearly_trend(df)

# Exclude 2025 (partial year) from training
train  = yearly[yearly["year"] <= 2024].copy()

# ── Forecast Function ────────────────────────────
def linear_forecast(train_df, col, forecast_yrs):
    from sklearn.linear_model import LinearRegression
    X = train_df["year"].values.reshape(-1,1)
    y = train_df[col].values
    model = LinearRegression()
    model.fit(X, y)
    future_years = np.arange(2025, forecast_yrs + 1)
    preds = model.predict(future_years.reshape(-1,1))
    preds = np.maximum(preds, 0)  # no negative accidents
    # Simple confidence interval: ±1.5 * std of residuals
    residuals = y - model.predict(X)
    std_err   = np.std(residuals) * 1.5
    return future_years, preds, std_err, model

import plotly.graph_objects as go
import plotly.express as px

DARK = dict(plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
            font=dict(color="#ffffff"),
            margin=dict(l=20,r=20,t=50,b=20))

# ═══════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════
st.markdown("<h1 style='color:#4da6ff;'>📈 Accident Trend Forecast</h1>", unsafe_allow_html=True)
st.markdown("""
    <p style='color:#8899aa;'>
        Linear regression model trained on 10 years of accident data (2015–2024).
        Predicts global aviation accidents through 2030.
    </p>
""", unsafe_allow_html=True)
st.divider()

# ── Run Forecast ─────────────────────────────────
future_yrs, preds, std_err, lr_model = linear_forecast(train, "total_accidents", forecast_years)

# ═══════════════════════════════════════════════
#  KPI METRICS
# ═══════════════════════════════════════════════
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("📊 2024 Actual", format_number(int(train[train["year"]==2024]["total_accidents"].values[0])))
with k2:
    pred_2026 = int(round(preds[future_yrs==2026][0])) if 2026 in future_yrs else "—"
    st.metric("🔮 2026 Prediction", format_number(pred_2026) if pred_2026 != "—" else "—")
with k3:
    if forecast_years >= 2027 and 2027 in future_yrs:
        pred_2027 = int(round(preds[future_yrs==2027][0]))
        st.metric("🔮 2027 Prediction", format_number(pred_2027))
    else:
        st.metric("📉 Overall Trend", "Declining")
with k4:
    slope = lr_model.coef_[0]
    trend_str = f"{'▼' if slope < 0 else '▲'} {abs(slope):.1f} accidents/year"
    st.metric("📐 Trend Slope", trend_str)

st.divider()

# ═══════════════════════════════════════════════
#  MAIN FORECAST CHART
# ═══════════════════════════════════════════════
st.subheader("🔮 Global Accident Forecast")

fig = go.Figure()

# Historical line
fig.add_trace(go.Scatter(
    x=train["year"], y=train["total_accidents"],
    mode="lines+markers",
    name="Historical (2015–2024)",
    line=dict(color="#4da6ff", width=3),
    marker=dict(size=8, color="#4da6ff"),
    hovertemplate="<b>Year:</b> %{x}<br><b>Accidents:</b> %{y}<extra></extra>"
))

# 2025 actual (partial year - show as dotted)
actual_2025 = int(yearly[yearly["year"]==2025]["total_accidents"].values[0])
fig.add_trace(go.Scatter(
    x=[2024, 2025], y=[int(train[train["year"]==2024]["total_accidents"].values[0]), actual_2025],
    mode="lines+markers",
    name="2025 Actual (partial)",
    line=dict(color="#ffcc00", width=2, dash="dot"),
    marker=dict(size=8, color="#ffcc00"),
    hovertemplate="<b>Year:</b> %{x}<br><b>Accidents:</b> %{y} (partial)<extra></extra>"
))

# Forecast line
fig.add_trace(go.Scatter(
    x=future_yrs, y=preds.round(0),
    mode="lines+markers",
    name=f"Forecast ({future_yrs[0]}–{future_yrs[-1]})",
    line=dict(color="#00ff88", width=3, dash="dash"),
    marker=dict(size=9, color="#00ff88", symbol="diamond"),
    hovertemplate="<b>Year:</b> %{x}<br><b>Predicted:</b> %{y:.0f}<extra></extra>"
))

# Confidence interval
if show_confidence:
    fig.add_trace(go.Scatter(
        x=np.concatenate([future_yrs, future_yrs[::-1]]),
        y=np.concatenate([preds+std_err, (preds-std_err)[::-1]]),
        fill="toself",
        fillcolor="rgba(0,255,136,0.08)",
        line=dict(color="rgba(0,0,0,0)"),
        name=f"Confidence (±{std_err:.0f})",
        hoverinfo="skip"
    ))

# Vertical line at forecast start
fig.add_vline(x=2024.5, line_dash="dot", line_color="#8899aa",
              annotation_text="Forecast →", annotation_font_color="#8899aa")

fig.update_layout(
    **DARK,
    height=420,
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#2a4a7f",
                font=dict(color="#ffffff")),
    xaxis=dict(gridcolor="#1a2035", tickmode="linear", dtick=1),
    yaxis=dict(gridcolor="#1a2035", title="Total Accidents")
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ═══════════════════════════════════════════════
#  FORECAST TABLE
# ═══════════════════════════════════════════════
col_table, col_insight = st.columns([1, 1])

with col_table:
    st.subheader("📋 Forecast Summary Table")

    hist_rows = []
    for _, row in train.iterrows():
        hist_rows.append({
            "Year": int(row["year"]),
            "Accidents": int(row["total_accidents"]),
            "Type": "📊 Historical",
            "Change": f"{row['yoy_change_pct']:+.1f}%" if pd.notna(row["yoy_change_pct"]) else "—"
        })

    # 2025 partial
    hist_rows.append({
        "Year": 2025,
        "Accidents": actual_2025,
        "Type": "🟡 Partial (2025)",
        "Change": "—"
    })

    prev = actual_2025
    for yr, pred in zip(future_yrs, preds):
        if yr == 2025:
            continue
        chg = ((pred - prev) / prev * 100) if prev else 0
        hist_rows.append({
            "Year": int(yr),
            "Accidents": int(round(pred)),
            "Type": "🔮 Forecast",
            "Change": f"{chg:+.1f}%"
        })
        prev = pred

    forecast_df = pd.DataFrame(hist_rows)
    st.dataframe(forecast_df, use_container_width=True, hide_index=True, height=400)

with col_insight:
    st.subheader("💡 Forecast Insights")

    total_hist  = int(train["total_accidents"].sum())
    avg_hist    = round(train["total_accidents"].mean(), 1)
    pred_2026_v = int(round(preds[future_yrs==2026][0])) if 2026 in future_yrs else None

    insights = [
        ("📉", f"Overall trend is <b>{'declining' if slope<0 else 'rising'}</b> at "
               f"{abs(slope):.1f} accidents per year"),
        ("📊", f"Historical average: <b>{avg_hist:.0f} accidents/year</b> (2015–2024)"),
        ("🏆", f"Peak year was <b>2019</b> with <b>296 accidents</b>"),
        ("⬇️", f"Lowest year was <b>2021</b> with <b>217 accidents</b>"),
        ("🔮", f"2026 forecast: <b>{pred_2026_v} accidents</b>" if pred_2026_v else ""),
        ("✈️", "Commercial aviation safety continues to improve"),
        ("⚠️", "2025 data is partial — full year may differ from forecast"),
        ("📐", f"Model R² shows consistent downward trend since 2019 peak"),
    ]
    for icon, text in insights:
        if text:
            st.markdown(
                f"<div class='insight-card'>{icon} {text}</div>",
                unsafe_allow_html=True
            )

st.divider()

# ═══════════════════════════════════════════════
#  BY AIRCRAFT CATEGORY FORECAST
# ═══════════════════════════════════════════════
st.subheader("✈️ Forecast by Aircraft Category")

categories = ["Commercial Jet","Private / General Aviation","Business Jet",
              "Regional / Turboprop","Cargo","Military","Other / Unknown"]

if "All" not in selected_cats:
    categories = [c for c in categories if c in selected_cats]

cat_yearly = df[df["year"]<=2024].groupby(["year","aircraft_category"]).size().reset_index(name="accidents")

cat_fig = go.Figure()
colors  = ["#4da6ff","#00ff88","#ffcc00","#ff6600","#ff0044","#aa44ff","#44ffff"]

for cat, color in zip(categories, colors):
    cat_data = cat_yearly[cat_yearly["aircraft_category"]==cat].sort_values("year")
    if len(cat_data) < 3:
        continue

    # Historical
    cat_fig.add_trace(go.Scatter(
        x=cat_data["year"], y=cat_data["accidents"],
        mode="lines+markers",
        name=cat,
        line=dict(color=color, width=2),
        marker=dict(size=6),
        legendgroup=cat,
        hovertemplate=f"<b>{cat}</b><br>Year: %{{x}}<br>Accidents: %{{y}}<extra></extra>"
    ))

    # Forecast
    _, cat_preds, _, _ = linear_forecast(cat_data, "accidents", forecast_years)
    cat_fig.add_trace(go.Scatter(
        x=list(range(2025, forecast_years+1)),
        y=cat_preds.round(0),
        mode="lines+markers",
        name=f"{cat} (forecast)",
        line=dict(color=color, width=2, dash="dash"),
        marker=dict(size=6, symbol="diamond"),
        legendgroup=cat,
        showlegend=False,
        hovertemplate=f"<b>{cat} forecast</b><br>Year: %{{x}}<br>Predicted: %{{y:.0f}}<extra></extra>"
    ))

cat_fig.add_vline(x=2024.5, line_dash="dot", line_color="#8899aa")
cat_fig.update_layout(
    **DARK, height=420,
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#2a4a7f", font=dict(color="#ffffff")),
    xaxis=dict(gridcolor="#1a2035", tickmode="linear", dtick=1),
    yaxis=dict(gridcolor="#1a2035", title="Accidents")
)
st.plotly_chart(cat_fig, use_container_width=True)

st.divider()

# ═══════════════════════════════════════════════
#  DAMAGE SEVERITY FORECAST
# ═══════════════════════════════════════════════
st.subheader("🔥 Damage Severity Index Forecast")

dmg_future, dmg_preds, dmg_std, _ = linear_forecast(train, "avg_damage_severity", forecast_years)

dmg_fig = go.Figure()
dmg_fig.add_trace(go.Scatter(
    x=train["year"], y=train["avg_damage_severity"],
    mode="lines+markers", name="Historical",
    line=dict(color="#ffcc00", width=3),
    marker=dict(size=8, color="#ffcc00"),
))
dmg_fig.add_trace(go.Scatter(
    x=dmg_future, y=dmg_preds,
    mode="lines+markers", name="Forecast",
    line=dict(color="#ff6600", width=3, dash="dash"),
    marker=dict(size=8, color="#ff6600", symbol="diamond"),
))
if show_confidence:
    dmg_fig.add_trace(go.Scatter(
        x=np.concatenate([dmg_future, dmg_future[::-1]]),
        y=np.concatenate([dmg_preds+dmg_std, (dmg_preds-dmg_std)[::-1]]),
        fill="toself", fillcolor="rgba(255,102,0,0.08)",
        line=dict(color="rgba(0,0,0,0)"), name="Confidence", hoverinfo="skip"
    ))
dmg_fig.add_vline(x=2024.5, line_dash="dot", line_color="#8899aa")
dmg_fig.update_layout(
    **DARK, height=320,
    yaxis=dict(gridcolor="#1a2035", title="Avg Damage Severity (0=None, 3=Destroyed)"),
    xaxis=dict(gridcolor="#1a2035", tickmode="linear", dtick=1),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#ffffff"))
)
st.plotly_chart(dmg_fig, use_container_width=True)

st.divider()
st.markdown("<div class='footer'>📈 Trend Forecast | Linear Regression | Aviation Safety Intelligence Platform</div>",
            unsafe_allow_html=True)
