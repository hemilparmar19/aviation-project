import streamlit as st
import pandas as pd
import numpy as np
import pickle, json, os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_loader import (load_main, load_risk_weighted,
                                load_crash_risk, load_high_risk_prob)
from utils.helpers import risk_emoji, risk_label, risk_color, format_number

st.set_page_config(page_title="AI Risk Predictor | Aviation Safety",
                   page_icon="🤖", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_path):
         with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

# ── Load ML Model ────────────────────────────────
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

@st.cache_resource
def load_model():
    with open(os.path.join(MODEL_DIR, "risk_model.pkl"), "rb") as f:
        model = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "le_aircraft.pkl"), "rb") as f:
        le_aircraft = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "le_country.pkl"), "rb") as f:
        le_country = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "feature_cols.pkl"), "rb") as f:
        feature_cols = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "model_meta.json"), "r") as f:
        meta = json.load(f)
    return model, le_aircraft, le_country, feature_cols, meta

model, le_aircraft, le_country, feature_cols, meta = load_model()

# ── Load Data for lookups ────────────────────────
df       = load_main()
risk_w   = load_risk_weighted()
crash_r  = load_crash_risk()
high_r   = load_high_risk_prob()

MONTH_NAMES = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]
SEV_LABELS  = {0:"Non-Fatal", 1:"Low", 2:"Medium", 3:"High"}
SEV_COLORS  = {0:"#00ff88",   1:"#ffcc00", 2:"#ff6600", 3:"#ff0044"}

# ── Sidebar ──────────────────────────────────────
with st.sidebar:
    st.markdown("<h3 style='color:#00a8ff; font-family:\"Share Tech Mono\",monospace; "
                "text-shadow:0 0 8px rgba(0,168,255,0.3);'>AVIATION SAFETY</h3>",
                unsafe_allow_html=True)
    st.divider()
    st.markdown(f"""
        <div style='background:#0a0f14;padding:14px;border-radius:10px;
                    border:1px solid rgba(0,168,255,0.2);'>
            <p style='color:#7a8a9a;margin:0;font-size:0.78rem;'>🤖 MODEL</p>
            <p style='color:#00a8ff;margin:4px 0 0 0;font-weight:600;'>Random Forest</p>
            <p style='color:#7a8a9a;margin:8px 0 0 0;font-size:0.78rem;'>🎯 ACCURACY</p>
            <p style='color:#00a8ff;margin:4px 0 0 0;font-weight:600;'>{meta['accuracy']}%</p>
            <p style='color:#7a8a9a;margin:8px 0 0 0;font-size:0.78rem;'>🌲 ESTIMATORS</p>
            <p style='color:#e0e0e0;margin:4px 0 0 0;font-weight:600;'>200 trees</p>
            <p style='color:#7a8a9a;margin:8px 0 0 0;font-size:0.78rem;'>📊 TRAINING DATA</p>
            <p style='color:#e0e0e0;margin:4px 0 0 0;font-weight:600;'>2,076 records</p>
            <p style='color:#7a8a9a;margin:8px 0 0 0;font-size:0.78rem;'>🧪 TEST DATA</p>
            <p style='color:#e0e0e0;margin:4px 0 0 0;font-weight:600;'>520 records</p>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("""
        <div style='color:#7a8a9a;font-size:0.8rem;'>
            <b style='color:#e0e0e0;'>Features Used:</b><br>
            • Aircraft Category<br>
            • Country Risk Score<br>
            • Month of Travel<br>
            • Overall Risk Score<br>
            • Avg Fatal Risk<br>
            • High Risk Probability<br>
            • Avg Annual Crashes<br>
            • Severe Damage Rate
        </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════
st.markdown("<h1 style='color:#00a8ff; text-shadow:0 0 15px rgba(0,168,255,0.3);'>🤖 AI Accident Risk Predictor</h1>",
            unsafe_allow_html=True)
st.markdown("""
    <p style='color:#7a8a9a;'>
        Our Random Forest model — trained on 2,596 real accidents (2015–2025) —
        predicts fatality severity based on country, aircraft type, and travel month.
        Uses risk scores from all 4 data tables.
    </p>
""", unsafe_allow_html=True)

st.divider()

# ═══════════════════════════════════════════════
#  INPUT FORM + PREDICTION
# ═══════════════════════════════════════════════
col_form, col_result = st.columns([1, 1.2], gap="large")

with col_form:
    st.markdown("### ✈️ Enter Flight Details")

    selected_country = st.selectbox(
        "🌍 Country / Region",
        options=sorted(df["country_clean"].unique().tolist()),
        index=sorted(df["country_clean"].unique().tolist()).index("United States")
    )

    selected_aircraft = st.selectbox(
        "✈️ Aircraft Category",
        options=sorted(df["aircraft_category"].unique().tolist()),
        index=sorted(df["aircraft_category"].unique().tolist()).index("Commercial Jet")
    )

    selected_month_name = st.selectbox(
        "📅 Month of Travel",
        options=MONTH_NAMES,
        index=0
    )
    selected_month = MONTH_NAMES.index(selected_month_name) + 1

    selected_cause = st.selectbox(
        "⚠️ Primary Risk Concern (optional)",
        options=["Not Specified"] + sorted(df["reason_clean"].unique().tolist()),
        index=0
    )

    st.markdown("<br>", unsafe_allow_html=True)
    predict_btn = st.button("🔮 Predict Risk", use_container_width=True)

    # Show historical context
    st.divider()
    st.markdown("### 📊 Historical Context")
    country_hist = df[df["country_clean"] == selected_country]
    aircraft_hist = df[df["aircraft_category"] == selected_aircraft]

    h1, h2 = st.columns(2)
    with h1:
        st.metric("Accidents in " + selected_country[:12],
                  format_number(len(country_hist)))
        fatal_c = round((country_hist["fat."] > 0).sum() / len(country_hist) * 100, 1) if len(country_hist) else 0
        st.metric("Fatal % (Country)", f"{fatal_c}%")
    with h2:
        st.metric("Accidents for Aircraft Type",
                  format_number(len(aircraft_hist)))
        fatal_a = round((aircraft_hist["fat."] > 0).sum() / len(aircraft_hist) * 100, 1) if len(aircraft_hist) else 0
        st.metric("Fatal % (Aircraft)", f"{fatal_a}%")

# ─────────────────────────────────────────────
#  PREDICTION LOGIC
# ─────────────────────────────────────────────
with col_result:
    st.markdown("### 🎯 Risk Assessment")

    if not predict_btn:
        st.markdown("""
            <div style='background:#0a0f14;border-radius:14px;padding:40px;
                        border:1px dashed rgba(0,168,255,0.2);text-align:center;margin-top:10px;'>
                <div style='font-size:3rem;'>🔮</div>
                <h3 style='color:#7a8a9a;'>Awaiting Prediction</h3>
                <p style='color:#7a8a9a;font-size:0.9rem;'>
                    Fill in the flight details on the left<br>
                    and click <b style='color:#00a8ff;'>Predict Risk</b>
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Fetch risk scores from lookup tables
        rw_row   = risk_w[risk_w["country_clean"] == selected_country]
        cr_row   = crash_r[crash_r["country_clean"] == selected_country]
        hr_row   = high_r[high_r["country_clean"] == selected_country]

        overall_risk_score    = float(rw_row["overall_risk_score"].values[0])    if len(rw_row) else 0.3
        avg_fatal_risk        = float(rw_row["avg_fatal_risk"].values[0])        if len(rw_row) else 0.2
        severe_damage_rate    = float(rw_row["severe_damage_rate"].values[0])    if len(rw_row) else 0.5
        country_risk_score    = float(cr_row["country_risk_score"].values[0])    if len(cr_row) else 0.1
        avg_annual_crashes    = float(cr_row["avg_annual_crashes"].values[0])    if len(cr_row) else 5.0
        high_risk_probability = float(hr_row["high_risk_probability"].values[0]) if len(hr_row) else 0.3

        # Encode inputs
        try:
            aircraft_enc = le_aircraft.transform([selected_aircraft])[0]
        except ValueError:
            aircraft_enc = 0
        try:
            country_enc = le_country.transform([selected_country])[0]
        except ValueError:
            country_enc = 0

        # Build feature vector (same order as training)
        input_data = pd.DataFrame([[
            aircraft_enc,
            country_enc,
            selected_month,
            overall_risk_score,
            avg_fatal_risk,
            country_risk_score,
            high_risk_probability,
            avg_annual_crashes,
            severe_damage_rate
        ]], columns=feature_cols)

        # Predict
        pred_class       = model.predict(input_data)[0]
        pred_proba       = model.predict_proba(input_data)[0]
        pred_label       = SEV_LABELS[pred_class]
        pred_color       = SEV_COLORS[pred_class]
        confidence       = round(pred_proba[pred_class] * 100, 1)
        risk_pct_overall = round(overall_risk_score * 100, 1)

        # Global averages for comparison
        global_fatal_pct = round((df["fat."] > 0).sum() / len(df) * 100, 1)
        country_fatal_pct = round((df[df["country_clean"]==selected_country]["fat."]>0).sum() /
                                   max(len(df[df["country_clean"]==selected_country]),1) * 100, 1)

        # ── RESULT CARD ───────────────────────────
        st.markdown(f"""
            <div style='background:linear-gradient(135deg,#0a0f14,#0d1128);
                        border-radius:14px;padding:28px;
                        border:2px solid {pred_color};margin-bottom:16px;'>
                <div style='text-align:center;'>
                    <div style='font-size:3rem;'>
                        {risk_emoji(risk_pct_overall)}
                    </div>
                    <h2 style='color:{pred_color};margin:8px 0 4px 0;font-size:1.8rem;'>
                        {pred_label}
                    </h2>
                    <p style='color:#7a8a9a;margin:0;font-size:0.9rem;'>
                        Predicted Fatality Severity
                    </p>
                    <div style='background:#060a0f;border-radius:20px;
                                padding:6px 20px;display:inline-block;margin-top:10px;'>
                        <span style='color:{pred_color};font-weight:600;font-size:1.1rem;'>
                            {confidence}% confidence
                        </span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # ── PROBABILITY BREAKDOWN ─────────────────
        st.markdown("#### 📊 Probability Breakdown")
        for i, (label, prob) in enumerate(zip(SEV_LABELS.values(), pred_proba)):
            pct = round(prob * 100, 1)
            color = SEV_COLORS[i]
            st.markdown(f"""
                <div style='margin-bottom:10px;'>
                    <div style='display:flex;justify-content:space-between;margin-bottom:4px;'>
                        <span style='color:#e0e0e0;font-size:0.88rem;'>{label}</span>
                        <span style='color:{color};font-weight:600;font-size:0.88rem;'>{pct}%</span>
                    </div>
                    <div style='background:#060a0f;border-radius:6px;height:8px;'>
                        <div style='background:{color};border-radius:6px;
                                    height:8px;width:{pct}%;transition:width 0.5s;'></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.divider()

        # ── COUNTRY RISK METRICS ──────────────────
        st.markdown("#### 🌍 Country Risk Profile")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Overall Risk Score",
                      f"{risk_pct_overall}%",
                      delta_color="inverse")
        with m2:
            st.metric("Avg Fatal Risk",
                      f"{round(avg_fatal_risk*100,1)}%",
                      delta_color="inverse")
        with m3:
            st.metric("High Risk Probability",
                      f"{round(high_risk_probability*100,1)}%",
                      delta_color="inverse")

        st.divider()

        # ── COMPARISON VS GLOBAL ──────────────────
        st.markdown("#### 📈 Your Scenario vs Global Average")
        comp_df = pd.DataFrame({
            "Metric": ["Fatal Accident %", "Risk Score"],
            "Your Scenario": [country_fatal_pct, risk_pct_overall],
            "Global Average": [global_fatal_pct, 30.0]
        })

        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Your Scenario",
            x=comp_df["Metric"],
            y=comp_df["Your Scenario"],
            marker_color=pred_color
        ))
        fig.add_trace(go.Bar(
            name="Global Average",
            x=comp_df["Metric"],
            y=comp_df["Global Average"],
            marker_color="#00a8ff"
        ))
        fig.update_layout(
            barmode="group",
            plot_bgcolor="#0a0f14",
            paper_bgcolor="#0a0f14",
            font=dict(color="#e0e0e0"),
            height=250,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════
#  KEY RISK FACTORS (Feature Importance)
# ═══════════════════════════════════════════════
st.divider()
st.markdown("### 🔑 What Drives Risk? (Feature Importance)")

importances = model.feature_importances_
feat_names  = ["Aircraft Type","Country","Month","Overall Risk Score",
               "Avg Fatal Risk","Country Risk Score","High Risk Prob",
               "Annual Crashes","Severe Damage Rate"]

imp_df = pd.DataFrame({
    "Feature":    feat_names,
    "Importance": (importances * 100).round(1)
}).sort_values("Importance", ascending=True)

import plotly.express as px
fig_imp = px.bar(
    imp_df, x="Importance", y="Feature", orientation="h",
    color="Importance",
    color_continuous_scale=[[0,"#0d1128"],[0.5,"#00a8ff"],[1,"#00ff88"]],
    labels={"Importance":"Importance (%)","Feature":""},
    title="Feature Importance — Random Forest Model"
)
fig_imp.update_coloraxes(showscale=False)
fig_imp.update_layout(
    plot_bgcolor="#0a0f14", paper_bgcolor="#0a0f14",
    font=dict(color="#e0e0e0"),
    xaxis=dict(gridcolor="#0a0f14"),
    yaxis=dict(gridcolor="#0a0f14"),
    height=360,
    margin=dict(l=10,r=10,t=40,b=10)
)
st.plotly_chart(fig_imp, use_container_width=True)

# ═══════════════════════════════════════════════
#  SCENARIO COMPARISON TOOL
# ═══════════════════════════════════════════════
st.divider()
st.markdown("### 🔄 Compare Two Scenarios")
st.markdown("<p style='color:#7a8a9a;'>Compare risk predictions for two different flight configurations side by side.</p>",
            unsafe_allow_html=True)

sc1, sc2 = st.columns(2)
scenarios = []
for col, label, def_country in [(sc1,"Scenario A","United States"),
                                  (sc2,"Scenario B","Dominican Republic")]:
    with col:
        st.markdown(f"**{label}**")
        s_country  = st.selectbox(f"Country ({label})",
                                   sorted(df["country_clean"].unique().tolist()),
                                   index=sorted(df["country_clean"].unique().tolist()).index(def_country),
                                   key=f"sc_{label}_country")
        s_aircraft = st.selectbox(f"Aircraft ({label})",
                                   sorted(df["aircraft_category"].unique().tolist()),
                                   key=f"sc_{label}_aircraft")
        s_month    = st.selectbox(f"Month ({label})", MONTH_NAMES, key=f"sc_{label}_month")
        scenarios.append((s_country, s_aircraft, MONTH_NAMES.index(s_month)+1, label))

if st.button("⚡ Compare Scenarios", use_container_width=True):
    results = []
    for s_country, s_aircraft, s_month, s_label in scenarios:
        rw  = risk_w[risk_w["country_clean"]==s_country]
        cr  = crash_r[crash_r["country_clean"]==s_country]
        hr  = high_r[high_r["country_clean"]==s_country]
        try: a_enc = le_aircraft.transform([s_aircraft])[0]
        except: a_enc = 0
        try: c_enc = le_country.transform([s_country])[0]
        except: c_enc = 0

        inp = pd.DataFrame([[
            a_enc, c_enc, s_month,
            float(rw["overall_risk_score"].values[0]) if len(rw) else 0.3,
            float(rw["avg_fatal_risk"].values[0])     if len(rw) else 0.2,
            float(cr["country_risk_score"].values[0]) if len(cr) else 0.1,
            float(hr["high_risk_probability"].values[0]) if len(hr) else 0.3,
            float(cr["avg_annual_crashes"].values[0]) if len(cr) else 5.0,
            float(rw["severe_damage_rate"].values[0]) if len(rw) else 0.5
        ]], columns=feature_cols)

        pc   = model.predict(inp)[0]
        pp   = model.predict_proba(inp)[0]
        results.append({
            "label":      s_label,
            "country":    s_country,
            "aircraft":   s_aircraft,
            "month":      MONTH_NAMES[s_month-1],
            "pred_class": pc,
            "pred_label": SEV_LABELS[pc],
            "confidence": round(pp[pc]*100,1),
            "color":      SEV_COLORS[pc],
            "proba":      pp
        })

    r1, r2 = st.columns(2)
    for col, res in zip([r1, r2], results):
        with col:
            st.markdown(f"""
                <div style='background:#0a0f14;border-radius:12px;padding:20px;
                            border:2px solid {res["color"]};text-align:center;'>
                    <h4 style='color:#7a8a9a;margin:0;'>{res["label"]}</h4>
                    <p style='color:#e0e0e0;margin:4px 0;font-size:0.85rem;'>
                        {res["country"]} | {res["aircraft"]} | {res["month"]}
                    </p>
                    <div style='font-size:2rem;margin:10px 0;'>
                        {risk_emoji(res["pred_class"]*25)}
                    </div>
                    <h3 style='color:{res["color"]};margin:0;'>{res["pred_label"]}</h3>
                    <p style='color:#7a8a9a;margin:4px 0;font-size:0.85rem;'>
                        {res["confidence"]}% confidence
                    </p>
                </div>
            """, unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────
st.divider()
st.markdown("<div class='footer' style='color:#7a8a9a;'>🤖 AI Risk Predictor | Random Forest | 70.38% Accuracy | Aviation Safety Intelligence Platform</div>",
            unsafe_allow_html=True)
