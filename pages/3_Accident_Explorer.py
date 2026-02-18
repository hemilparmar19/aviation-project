import streamlit as st
import pandas as pd
import re, os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_loader import load_main, load_risk_weighted
from utils.helpers import risk_emoji, format_number

st.set_page_config(page_title="Accident Explorer | Aviation Safety",
                   page_icon="🔍", layout="wide")

def load_css():
    css_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "style.css"))
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

# ── Load Data ────────────────────────────────────
df     = load_main()
risk_w = load_risk_weighted()
df = df.merge(risk_w[["country_clean","overall_risk_score"]], on="country_clean", how="left")

# Clean NaN values upfront so they never show as "nan"
df["dmg_clean"] = df["dmg_clean"].fillna("Unknown")
df["operator"]  = df["operator"].fillna("Unknown")
df["type"]      = df["type"].fillna("Unknown")

# ── Sidebar ──────────────────────────────────────
with st.sidebar:
    st.markdown("<h3 style='color:#4da6ff;'>✈️ Aviation Safety</h3>", unsafe_allow_html=True)
    st.divider()
    st.markdown("**🔽 Explorer Filters**")
    year_range = st.slider("Year Range", 2015, 2025, (2015, 2025))
    selected_countries = st.multiselect(
        "Country", options=["All"] + sorted(df["country_clean"].unique().tolist()), default=["All"])
    selected_aircraft = st.multiselect(
        "Aircraft Category", options=["All"] + sorted(df["aircraft_category"].unique().tolist()), default=["All"])
    selected_causes = st.multiselect(
        "Accident Cause", options=["All"] + sorted(df["reason_clean"].unique().tolist()), default=["All"])
    selected_severity = st.multiselect(
        "Fatality Severity", options=["All","Non-Fatal","Low","Medium","High"], default=["All"])
    selected_damage = st.multiselect(
        "Damage Level", options=["All"] + sorted(df["dmg_clean"].unique().tolist()), default=["All"])
    st.divider()
    sort_col = st.selectbox("Sort By", ["acc._date","fat.","country_clean","aircraft_category","reason_clean"])
    sort_asc = st.radio("Sort Order", ["Descending","Ascending"]) == "Ascending"

# ── STEP 1: Apply Sidebar Filters ───────────────
mask = df["year"].between(year_range[0], year_range[1])
if "All" not in selected_countries:  mask &= df["country_clean"].isin(selected_countries)
if "All" not in selected_aircraft:   mask &= df["aircraft_category"].isin(selected_aircraft)
if "All" not in selected_causes:     mask &= df["reason_clean"].isin(selected_causes)
if "All" not in selected_severity:   mask &= df["Fatality_Severity"].isin(selected_severity)
if "All" not in selected_damage:     mask &= df["dmg_clean"].isin(selected_damage)
sidebar_filtered = df[mask].sort_values(sort_col, ascending=sort_asc).reset_index(drop=True)

# ── STEP 2: Apply Search on top of sidebar ──────
search = st.text_input("🔎 Search across all fields",
                        placeholder="Type country, airline, location, aircraft type...",
                        label_visibility="collapsed")

# THIS is the variable used everywhere - always reflects both sidebar + search
if search.strip():
    s   = search.lower().strip()
    pat = rf"\b{re.escape(s)}"
    sm  = (sidebar_filtered["country_clean"].str.lower().str.contains(pat, na=False, regex=True) |
           sidebar_filtered["aircraft_category"].str.lower().str.contains(pat, na=False, regex=True) |
           sidebar_filtered["reason_clean"].str.lower().str.contains(pat, na=False, regex=True) |
           sidebar_filtered["location"].str.lower().str.contains(pat, na=False, regex=True) |
           sidebar_filtered["Fatality_Severity"].str.lower().str.contains(pat, na=False, regex=True) |
           sidebar_filtered["operator"].str.lower().str.contains(pat, na=False, regex=True) |
           sidebar_filtered["type"].str.lower().str.contains(pat, na=False, regex=True))
    final = sidebar_filtered[sm].reset_index(drop=True)
    st.markdown(f"<p style='color:#ffcc00;'>🔎 <b>{len(final)}</b> results for <b>\"{search}\"</b></p>",
                unsafe_allow_html=True)
else:
    final = sidebar_filtered.copy()

# ═══════════════════════════════════════════════
#  HEADER — all stats use `final`
# ═══════════════════════════════════════════════
st.markdown("<h1 style='color:#4da6ff;'>🔍 Accident Explorer</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8899aa;'>Search, filter and explore all 2,596 accidents.</p>",
            unsafe_allow_html=True)

s1, s2, s3, s4, s5 = st.columns(5)
with s1: st.metric("🔎 Results Found",   format_number(len(final)))
with s2: st.metric("💀 Total Fatalities", format_number(int(final["fat."].sum())))
with s3:
    fp = round((final["fat."] > 0).sum() / max(len(final),1) * 100, 1)
    st.metric("⚠️ Fatal %", f"{fp}%")
with s4:
    tc = final["country_clean"].value_counts().index[0] if len(final) else "—"
    st.metric("🌍 Top Country", tc)
with s5:
    tca = final["reason_clean"].value_counts().index[0] if len(final) else "—"
    st.metric("🔥 Top Cause", tca[:16]+"…" if len(tca)>16 else tca)

st.divider()

# ═══════════════════════════════════════════════
#  TABS — all use `final`
# ═══════════════════════════════════════════════
if len(final) == 0:
    st.warning("No accidents found. Try adjusting the filters or search.")
else:
    tab_table, tab_cards, tab_stats = st.tabs(["📋 Table View","🃏 Card View","📊 Quick Stats"])

    # ── TAB 1: TABLE ─────────────────────────────
    with tab_table:
        display_df = final[["acc._date","country_clean","aircraft_category",
                             "reason_clean","Fatality_Severity","dmg_clean",
                             "fat.","operator","location"]].copy()
        display_df.columns = ["Date","Country","Aircraft","Cause",
                               "Severity","Damage","Fatalities","Operator","Location"]

        def sev_style(val):
            return {"Non-Fatal":"color:#00ff88","Low":"color:#ffcc00",
                    "Medium":"color:#ff6600","High":"color:#ff0044;font-weight:bold"}.get(val,"")

        st.dataframe(display_df.style.applymap(sev_style, subset=["Severity"]),
                     use_container_width=True, height=420, hide_index=True)

        c1, c2, _ = st.columns([1,1,4])
        with c1:
            st.download_button("⬇️ Export CSV",
                               data=final.to_csv(index=False),
                               file_name=f"accidents_{year_range[0]}_{year_range[1]}.csv",
                               mime="text/csv")
        with c2:
            st.download_button("⬇️ Export JSON",
                               data=final.to_json(orient="records", indent=2),
                               file_name="accidents_filtered.json",
                               mime="application/json")

        st.divider()
        st.markdown("### 🔎 View Accident Details")
        st.markdown("<p style='color:#8899aa;font-size:0.9rem;'>Enter a row number to see full details.</p>",
                    unsafe_allow_html=True)

        col_sel, col_btn = st.columns([2,1])
        with col_sel:
            row_idx = st.number_input(
                f"Row number (1 to {len(final)})",
                min_value=1,
                max_value=max(len(final), 1),
                value=1,
                step=1
            )
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            show_detail = st.button("🔍 Show Details", use_container_width=True)

        if show_detail:
            row = final.iloc[row_idx - 1]
            rp  = round(float(row.get("overall_risk_score", 0)) * 100, 1)
            sc  = {"High":"#ff0044","Medium":"#ff6600",
                   "Low":"#ffcc00","Non-Fatal":"#00ff88"}.get(row["Fatality_Severity"],"#aaa")
            st.markdown(f"""
                <div style='background:linear-gradient(135deg,#1a2035,#1e3a5f);
                            border-radius:14px;padding:28px;
                            border:1px solid #2a4a7f;margin-top:16px;'>
                    <h3 style='color:#4da6ff;margin-top:0;'>
                        ✈️ Accident Report
                        <span style='font-size:0.85rem;color:#8899aa;font-weight:normal;'>
                            — Row {row_idx} of {len(final)}
                        </span>
                    </h3>
                    <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px;margin-top:16px;'>
                        <div><p style='color:#8899aa;margin:0;font-size:0.78rem;'>📅 DATE</p>
                             <p style='color:#fff;margin:0;font-weight:600;'>{str(row['acc._date'])[:10]}</p></div>
                        <div><p style='color:#8899aa;margin:0;font-size:0.78rem;'>🌍 COUNTRY</p>
                             <p style='color:#fff;margin:0;font-weight:600;'>{row['country_clean']}</p></div>
                        <div><p style='color:#8899aa;margin:0;font-size:0.78rem;'>✈️ AIRCRAFT</p>
                             <p style='color:#fff;margin:0;font-weight:600;'>{row['aircraft_category']}</p></div>
                        <div><p style='color:#8899aa;margin:0;font-size:0.78rem;'>⚠️ CAUSE</p>
                             <p style='color:#ffcc00;margin:0;font-weight:600;'>{row['reason_clean']}</p></div>
                        <div><p style='color:#8899aa;margin:0;font-size:0.78rem;'>💀 FATALITIES</p>
                             <p style='color:{"#ff0044" if row["fat."]>0 else "#00ff88"};margin:0;font-weight:600;'>
                             {int(row["fat."])} fatalities</p></div>
                        <div><p style='color:#8899aa;margin:0;font-size:0.78rem;'>⚡ SEVERITY</p>
                             <p style='color:{sc};margin:0;font-weight:600;'>{row['Fatality_Severity']}</p></div>
                        <div><p style='color:#8899aa;margin:0;font-size:0.78rem;'>🔧 DAMAGE</p>
                             <p style='color:#fff;margin:0;font-weight:600;'>{row.get('dmg_clean','Unknown')}</p></div>
                        <div><p style='color:#8899aa;margin:0;font-size:0.78rem;'>🏢 OPERATOR</p>
                             <p style='color:#fff;margin:0;font-weight:600;'>{str(row.get('operator','Unknown'))[:30]}</p></div>
                        <div><p style='color:#8899aa;margin:0;font-size:0.78rem;'>📍 LOCATION</p>
                             <p style='color:#fff;margin:0;font-weight:600;'>{str(row.get('location','Unknown'))[:35]}</p></div>
                    </div>
                    <div style='margin-top:20px;padding-top:16px;border-top:1px solid #2a4a7f;'>
                        <p style='color:#8899aa;margin:0 0 6px 0;font-size:0.78rem;'>🌍 COUNTRY RISK SCORE</p>
                        <div style='background:#0a0e1a;border-radius:8px;height:10px;width:100%;'>
                            <div style='background:{"#ff0044" if rp>60 else "#ff6600" if rp>40 else "#ffcc00" if rp>20 else "#00ff88"};
                                        border-radius:8px;height:10px;width:{min(rp,100)}%;'></div>
                        </div>
                        <p style='color:#c9d1d9;margin:4px 0 0 0;font-size:0.85rem;'>
                            {risk_emoji(rp)} {rp}% overall risk — {row['country_clean']}
                        </p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 🔗 Similar Accidents (Same Aircraft + Cause)")
            similar = df[(df["aircraft_category"] == row["aircraft_category"]) &
                         (df["reason_clean"]       == row["reason_clean"]) &
                         (df.index                 != final.index[row_idx-1])
                        ][["acc._date","country_clean","aircraft_category",
                            "reason_clean","Fatality_Severity","fat."]].head(5)
            if len(similar):
                similar.columns = ["Date","Country","Aircraft","Cause","Severity","Fatalities"]
                st.dataframe(similar, use_container_width=True, hide_index=True)
            else:
                st.info("No similar accidents found.")

    # ── TAB 2: CARDS ─────────────────────────────
    with tab_cards:
        st.markdown(f"<p style='color:#8899aa;'>Showing first 20 of {len(final)} results.</p>",
                    unsafe_allow_html=True)
        cards_df = final.head(20)
        for i in range(0, len(cards_df), 2):
            col_a, col_b = st.columns(2)
            for col, idx in zip([col_a, col_b], [i, i+1]):
                if idx < len(cards_df):
                    r  = cards_df.iloc[idx]
                    sc = {"Non-Fatal":"#00ff88","Low":"#ffcc00",
                          "Medium":"#ff6600","High":"#ff0044"}.get(r["Fatality_Severity"],"#aaa")
                    with col:
                        st.markdown(f"""
                            <div style='background:#1a2035;border-radius:12px;padding:18px;
                                        border:1px solid #2a4a7f;margin-bottom:12px;
                                        border-left:4px solid {sc};'>
                                <div style='display:flex;justify-content:space-between;'>
                                    <span style='color:#8899aa;font-size:0.78rem;'>{str(r["acc._date"])[:10]}</span>
                                    <span style='color:{sc};font-size:0.78rem;font-weight:600;
                                                 background:rgba(0,0,0,0.3);padding:2px 8px;
                                                 border-radius:20px;'>{r["Fatality_Severity"]}</span>
                                </div>
                                <h4 style='color:#4da6ff;margin:8px 0 4px 0;'>{r["country_clean"]}</h4>
                                <p style='color:#c9d1d9;margin:0;font-size:0.88rem;'>✈️ {r["aircraft_category"]}</p>
                                <p style='color:#ffcc00;margin:4px 0;font-size:0.85rem;'>⚠️ {r["reason_clean"]}</p>
                                <p style='color:{"#ff0044" if r["fat."]>0 else "#8899aa"};
                                          margin:4px 0;font-size:0.83rem;'>
                                    💀 {int(r["fat."])} fatalities &nbsp;|&nbsp; 🔧 {r["dmg_clean"]}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)

    # ── TAB 3: QUICK STATS ───────────────────────
    with tab_stats:
        st.markdown("### 📊 Statistics for Current Results")
        import plotly.express as px
        DARK = {"plot_bgcolor":"#0d1117","paper_bgcolor":"#0d1117",
                "font":{"color":"#ffffff"},"height":300,
                "margin":{"l":20,"r":20,"t":40,"b":20}}

        q1, q2 = st.columns(2)
        with q1:
            sdf = final["Fatality_Severity"].value_counts().reset_index()
            sdf.columns = ["Severity","Count"]
            fig = px.bar(sdf, x="Severity", y="Count", color="Severity",
                         color_discrete_map={"Non-Fatal":"#00ff88","Low":"#ffcc00",
                                             "Medium":"#ff6600","High":"#ff0044"},
                         title="By Severity")
            fig.update_layout(**DARK)
            st.plotly_chart(fig, use_container_width=True)
        with q2:
            cdf = final["reason_clean"].value_counts().reset_index()
            cdf.columns = ["Cause","Count"]
            fig2 = px.bar(cdf.head(8), x="Count", y="Cause", orientation="h", title="Top Causes")
            fig2.update_traces(marker_color="#4da6ff")
            fig2.update_layout(**DARK)
            st.plotly_chart(fig2, use_container_width=True)

        q3, q4 = st.columns(2)
        with q3:
            ydf = final.groupby("year").size().reset_index(name="Accidents")
            fig3 = px.line(ydf, x="year", y="Accidents", title="Yearly Trend", markers=True)
            fig3.update_traces(line_color="#4da6ff", marker_color="#4da6ff")
            fig3.update_layout(**DARK)
            st.plotly_chart(fig3, use_container_width=True)
        with q4:
            adf = final["aircraft_category"].value_counts().reset_index()
            adf.columns = ["Category","Count"]
            fig4 = px.pie(adf, values="Count", names="Category", title="By Aircraft", hole=0.4)
            fig4.update_layout(**DARK)
            st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.markdown("<div class='footer'>🔍 Accident Explorer | Aviation Safety Intelligence Platform</div>",
            unsafe_allow_html=True)
