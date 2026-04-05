import streamlit as st
import pandas as pd
import numpy as np
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.helpers import format_number, format_pct
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dynamic Analysis | Aviation Safety",
                   page_icon="📤", layout="wide")

# ═══════════════════════════════════════════════
#  HUD THEME CONSTANTS
# ═══════════════════════════════════════════════
HUD_PRIMARY   = "#00a8ff"
HUD_SECONDARY = "#00d4ff"
HUD_BG        = "#060a0f"
HUD_CARD_BG   = "#0a0f14"
HUD_TEXT       = "#e0e0e0"
HUD_SUBTEXT   = "#7a8a9a"
HUD_WARNING    = "#ff9500"
HUD_DANGER     = "#ff0044"
HUD_BORDER     = "rgba(0,168,255,0.2)"

DARK = dict(plot_bgcolor="#0a0f14", paper_bgcolor="#0a0f14",
            font=dict(color="#e0e0e0"),
            margin=dict(l=20, r=20, t=40, b=20))

GREEN_SCALE = [[0, "#003366"], [1, "#00a8ff"]]
HEATMAP_SCALE = [[0, "#0a0f1a"], [0.25, "#0d2244"], [0.5, "#1a4a6b"], [0.75, "#0088dd"], [1, "#00a8ff"]]

SEVERITY_COLORS = {
    "Non-Fatal": "#00a8ff",
    "Low": "#ff9500",
    "Medium": "#ff6600",
    "High": "#ff0044",
}

# ═══════════════════════════════════════════════
#  CSS INJECTION
# ═══════════════════════════════════════════════
def load_css():
    css_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "style.css"))
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.markdown(f"""
<style>
    .stApp {{
        background-color: {HUD_BG};
    }}
    .hud-kpi {{
        background: {HUD_CARD_BG};
        border: 1px solid {HUD_BORDER};
        border-radius: 8px;
        padding: 16px 12px;
        text-align: center;
    }}
    .hud-kpi .kpi-label {{
        color: {HUD_SUBTEXT};
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0;
        font-family: 'Courier New', monospace;
    }}
    .hud-kpi .kpi-value {{
        color: {HUD_PRIMARY};
        font-size: 1.5rem;
        font-weight: 700;
        margin: 4px 0 0 0;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 8px rgba(0,168,255,0.3);
    }}
    .hud-kpi .kpi-value.secondary {{
        color: {HUD_SECONDARY};
        text-shadow: 0 0 8px rgba(0,212,255,0.3);
    }}
    .hud-kpi .kpi-value.warning {{
        color: {HUD_WARNING};
        text-shadow: 0 0 8px rgba(255,149,0,0.3);
    }}
    .hud-section-title {{
        color: {HUD_PRIMARY};
        font-family: 'Courier New', monospace;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        border-bottom: 1px solid {HUD_BORDER};
        padding-bottom: 8px;
        margin-bottom: 16px;
    }}
    div[data-testid="stTabs"] button {{
        color: {HUD_SUBTEXT} !important;
        font-family: 'Courier New', monospace !important;
        letter-spacing: 1px;
    }}
    div[data-testid="stTabs"] button[aria-selected="true"] {{
        color: {HUD_PRIMARY} !important;
        border-bottom-color: {HUD_PRIMARY} !important;
    }}
    .col-map-card {{
        background: {HUD_CARD_BG};
        padding: 12px;
        border-radius: 8px;
        border-left: 3px solid {HUD_PRIMARY};
        text-align: center;
    }}
    .col-map-card .field {{
        color: {HUD_SUBTEXT};
        margin: 0;
        font-size: 0.7rem;
        font-family: 'Courier New', monospace;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .col-map-card .colname {{
        color: {HUD_PRIMARY};
        margin: 4px 0 0 0;
        font-weight: 600;
        font-family: 'Courier New', monospace;
    }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#  SIDEBAR BRANDING
# ═══════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
        <div style='text-align:center; padding:12px 0;'>
            <p style='color:{HUD_PRIMARY}; font-family:"Courier New",monospace;
                      font-size:1.1rem; letter-spacing:2px; margin:0;
                      text-shadow:0 0 10px rgba(0,168,255,0.4);'>
                AVIATION SAFETY HUD
            </p>
            <p style='color:{HUD_SUBTEXT}; font-size:0.7rem; margin:4px 0 0 0;
                      font-family:"Courier New",monospace; letter-spacing:1px;'>
                DYNAMIC ANALYSIS MODULE
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown(f"""
        <p style='color:{HUD_SUBTEXT}; font-size:0.75rem; font-family:"Courier New",monospace;'>
            Upload CSV/Excel data to generate<br>real-time aviation analytics.
        </p>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════
def smart_column_mapper(df):
    """Auto-detect which columns map to our expected fields"""
    cols = df.columns.str.lower()
    mapping = {}

    # Date column detection
    date_keywords = ['date', 'acc._date', 'accident_date', 'incident_date']
    for kw in date_keywords:
        matches = [c for c in df.columns if kw in c.lower()]
        if matches:
            mapping['date'] = matches[0]
            break

    # Country column detection
    country_keywords = ['country', 'nation', 'location', 'country_clean']
    for kw in country_keywords:
        matches = [c for c in df.columns if kw in c.lower()]
        if matches:
            mapping['country'] = matches[0]
            break

    # Fatality column detection
    fatal_keywords = ['fatal', 'death', 'fat.', 'fatalities', 'casualties']
    for kw in fatal_keywords:
        matches = [c for c in df.columns if kw in c.lower()]
        if matches:
            mapping['fatalities'] = matches[0]
            break

    # Severity column detection
    sev_keywords = ['severity', 'fatality_severity', 'level']
    for kw in sev_keywords:
        matches = [c for c in df.columns if kw in c.lower()]
        if matches:
            mapping['severity'] = matches[0]
            break

    # Aircraft category detection
    aircraft_keywords = ['aircraft', 'plane', 'type', 'aircraft_category']
    for kw in aircraft_keywords:
        matches = [c for c in df.columns if kw in c.lower()]
        if matches:
            mapping['aircraft'] = matches[0]
            break

    # Cause/Reason detection
    cause_keywords = ['cause', 'reason', 'reason_clean']
    for kw in cause_keywords:
        matches = [c for c in df.columns if kw in c.lower()]
        if matches:
            mapping['cause'] = matches[0]
            break

    return mapping


def generate_template():
    """Generate a sample CSV template"""
    template = pd.DataFrame({
        'acc._date': ['2024-01-15', '2024-02-20', '2024-03-10'],
        'country_clean': ['United States', 'India', 'Brazil'],
        'aircraft_category': ['Commercial Jet', 'Business Jet', 'Private / General Aviation'],
        'reason_clean': ['Runway Excursion', 'Engine Technical Failure', 'Stall Loss Of Control'],
        'Fatality_Severity': ['Non-Fatal', 'Low', 'High'],
        'fat.': [0, 5, 25],
        'dmg_clean': ['Minor', 'Substantial', 'Destroyed']
    })
    return template


def hud_kpi_card(label, value, style_class=""):
    """Render a single KPI card in HUD style"""
    return f"""
        <div class='hud-kpi'>
            <p class='kpi-label'>{label}</p>
            <p class='kpi-value {style_class}'>{value}</p>
        </div>
    """


def hud_chart_layout(fig, height=350, title=None):
    """Apply standard HUD layout to a plotly figure"""
    layout_args = {
        **DARK,
        "height": height,
        "xaxis": dict(gridcolor="#0a0f14", zerolinecolor="#0a0f14"),
        "yaxis": dict(gridcolor="#0a0f14", zerolinecolor="#0a0f14"),
    }
    if title:
        layout_args["title"] = dict(text=title, font=dict(color=HUD_PRIMARY, size=14,
                                                           family="Courier New, monospace"))
    fig.update_layout(**layout_args)
    return fig


# ═══════════════════════════════════════════════
#  PAGE HEADER
# ═══════════════════════════════════════════════
st.markdown(f"""
    <h1 style='color:{HUD_PRIMARY}; text-shadow:0 0 15px rgba(0,168,255,0.3);
               font-family:"Courier New",monospace; letter-spacing:2px;'>
        DYNAMIC ANALYSIS
    </h1>
    <p style='color:{HUD_SUBTEXT}; font-family:"Courier New",monospace; font-size:0.85rem;'>
        Upload your own aviation accident dataset (CSV or Excel) and instantly generate
        interactive charts and insights. This module operates independently.
    </p>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  TEMPLATE DOWNLOAD
# ═══════════════════════════════════════════════
col_info, col_template = st.columns([2, 1])

with col_info:
    st.markdown(f"""
        <div style='background:{HUD_CARD_BG}; border:1px solid {HUD_BORDER};
                    border-radius:8px; padding:16px;'>
            <p style='color:{HUD_PRIMARY}; font-family:"Courier New",monospace;
                      font-size:0.85rem; margin:0 0 8px 0; letter-spacing:1px;'>
                EXPECTED COLUMNS (FLEXIBLE NAMING)
            </p>
            <p style='color:{HUD_TEXT}; font-size:0.8rem; margin:0; line-height:1.8;'>
                <span style='color:{HUD_SECONDARY};'>DATE</span> &mdash;
                    <code style='color:{HUD_SUBTEXT};'>acc._date, date, accident_date</code><br>
                <span style='color:{HUD_SECONDARY};'>COUNTRY</span> &mdash;
                    <code style='color:{HUD_SUBTEXT};'>country, country_clean, nation</code><br>
                <span style='color:{HUD_SECONDARY};'>FATALITIES</span> &mdash;
                    <code style='color:{HUD_SUBTEXT};'>fat., fatalities, deaths</code><br>
                <span style='color:{HUD_SECONDARY};'>SEVERITY</span> &mdash;
                    <code style='color:{HUD_SUBTEXT};'>Fatality_Severity, severity</code><br>
                <span style='color:{HUD_SECONDARY};'>AIRCRAFT</span> &mdash;
                    <code style='color:{HUD_SUBTEXT};'>aircraft_category, aircraft</code><br>
                <span style='color:{HUD_SECONDARY};'>CAUSE</span> &mdash;
                    <code style='color:{HUD_SUBTEXT};'>reason_clean, cause</code>
            </p>
        </div>
    """, unsafe_allow_html=True)

with col_template:
    st.markdown("<br>", unsafe_allow_html=True)
    template_df = generate_template()
    st.download_button(
        "DOWNLOAD SAMPLE TEMPLATE",
        data=template_df.to_csv(index=False),
        file_name="aviation_accident_template.csv",
        mime="text/csv",
        use_container_width=True
    )

st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  FILE UPLOAD
# ═══════════════════════════════════════════════
st.markdown(f"<p class='hud-section-title'>DATA UPLOAD</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=['csv', 'xlsx', 'xls'],
    help="Upload aviation accident data in CSV or Excel format"
)

if uploaded_file is not None:
    try:
        # Read file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.markdown(f"""
            <div style='background:{HUD_CARD_BG}; border:1px solid {HUD_BORDER};
                        border-radius:8px; padding:10px 16px; margin:8px 0;'>
                <span style='color:{HUD_PRIMARY}; font-family:"Courier New",monospace;
                             font-size:0.8rem;'>
                    UPLOAD CONFIRMED &mdash; {uploaded_file.name} &mdash;
                    {format_number(len(df))} records loaded
                </span>
            </div>
        """, unsafe_allow_html=True)

        # ── Column Mapping ───────────────────────
        col_map = smart_column_mapper(df)

        if not col_map:
            st.markdown(f"""
                <div style='background:{HUD_CARD_BG}; border:1px solid rgba(255,149,0,0.4);
                            border-radius:8px; padding:16px; margin:12px 0;'>
                    <p style='color:{HUD_WARNING}; font-family:"Courier New",monospace;
                              font-size:0.85rem; margin:0;'>
                        WARNING: Could not auto-detect standard columns.
                        Ensure your data has columns for date, country, fatalities, etc.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Show detected mappings
            st.markdown(f"<p class='hud-section-title'>DETECTED COLUMN MAPPING</p>",
                        unsafe_allow_html=True)

            map_cols = st.columns(len(col_map))
            for i, (field, col_name) in enumerate(col_map.items()):
                with map_cols[i]:
                    st.markdown(f"""
                        <div class='col-map-card'>
                            <p class='field'>{field}</p>
                            <p class='colname'>{col_name}</p>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

            # ── Prepare date column ──────────────
            if 'date' in col_map:
                df[col_map['date']] = pd.to_datetime(df[col_map['date']], errors='coerce')
                df['_year'] = df[col_map['date']].dt.year
                df['_month'] = df[col_map['date']].dt.month

            # Ensure fatalities is numeric
            if 'fatalities' in col_map:
                df[col_map['fatalities']] = pd.to_numeric(df[col_map['fatalities']], errors='coerce')

            # ═══════════════════════════════════════
            #  KPI ROW
            # ═══════════════════════════════════════
            st.markdown(f"<p class='hud-section-title'>KEY PERFORMANCE INDICATORS</p>",
                        unsafe_allow_html=True)

            kpi_items = []
            kpi_items.append(("Total Records", format_number(len(df)), ""))

            if 'fatalities' in col_map:
                total_fat = df[col_map['fatalities']].sum()
                kpi_items.append(("Total Fatalities", format_number(total_fat) if not np.isnan(total_fat) else "N/A", "warning"))

            if 'fatalities' in col_map:
                fatal_mask = df[col_map['fatalities']] > 0
                fatal_pct = (fatal_mask.sum() / len(df) * 100) if len(df) > 0 else 0
                kpi_items.append(("Fatal %", f"{fatal_pct:.1f}%", "warning"))

            if 'country' in col_map:
                n_countries = df[col_map['country']].nunique()
                kpi_items.append(("Unique Countries", format_number(n_countries), "secondary"))

            if 'date' in col_map:
                yr_min = df['_year'].dropna().min()
                yr_max = df['_year'].dropna().max()
                date_range_str = f"{int(yr_min)}-{int(yr_max)}" if not np.isnan(yr_min) else "N/A"
                kpi_items.append(("Date Range", date_range_str, "secondary"))

            if 'aircraft' in col_map:
                most_common = df[col_map['aircraft']].mode()
                mc_val = most_common.iloc[0] if len(most_common) > 0 else "N/A"
                # Truncate long names
                mc_display = mc_val if len(str(mc_val)) <= 22 else str(mc_val)[:20] + ".."
                kpi_items.append(("Most Common Aircraft", mc_display, ""))

            kpi_cols = st.columns(len(kpi_items))
            for idx, (label, value, cls) in enumerate(kpi_items):
                with kpi_cols[idx]:
                    st.markdown(hud_kpi_card(label, value, cls), unsafe_allow_html=True)

            st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

            # ═══════════════════════════════════════
            #  TABBED DASHBOARD
            # ═══════════════════════════════════════
            tab1, tab2, tab3 = st.tabs([
                "OVERVIEW & TRENDS",
                "RISK & SEVERITY ANALYSIS",
                "DATA EXPLORER"
            ])

            # ─────────────────────────────────────
            #  TAB 1: OVERVIEW & TRENDS
            # ─────────────────────────────────────
            with tab1:

                # Yearly accident trend
                if 'date' in col_map:
                    try:
                        yearly = df.groupby('_year').size().reset_index(name='accidents')
                        yearly = yearly.dropna(subset=['_year'])

                        fig_trend = go.Figure()
                        fig_trend.add_trace(go.Scatter(
                            x=yearly['_year'], y=yearly['accidents'],
                            mode='lines+markers',
                            line=dict(color=HUD_PRIMARY, width=3),
                            marker=dict(size=7, color=HUD_PRIMARY),
                            fill='tozeroy',
                            fillcolor='rgba(0,168,255,0.07)',
                            name='Accidents'
                        ))
                        hud_chart_layout(fig_trend, 350, "YEARLY ACCIDENT TREND")
                        st.plotly_chart(fig_trend, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not generate yearly trend: {e}")

                # Year-over-year % change
                if 'date' in col_map:
                    try:
                        yearly = df.groupby('_year').size().reset_index(name='accidents')
                        yearly = yearly.dropna(subset=['_year']).sort_values('_year')
                        yearly['pct_change'] = yearly['accidents'].pct_change() * 100
                        yearly = yearly.dropna(subset=['pct_change'])

                        if len(yearly) > 1:
                            # Fewer accidents = good, so decrease (negative) is green
                            colors = [HUD_PRIMARY if v <= 0 else HUD_DANGER for v in yearly['pct_change']]
                            fig_yoy = go.Figure(data=[go.Bar(
                                x=yearly['_year'],
                                y=yearly['pct_change'],
                                marker_color=colors,
                                text=[f"{v:+.1f}%" for v in yearly['pct_change']],
                                textposition='outside',
                                textfont=dict(color=HUD_TEXT, size=10)
                            )])
                            hud_chart_layout(fig_yoy, 350, "YEAR-OVER-YEAR % CHANGE")
                            fig_yoy.update_layout(yaxis_title="% Change")
                            st.plotly_chart(fig_yoy, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not generate YoY chart: {e}")

                # Two-column row: countries & aircraft
                r2c1, r2c2 = st.columns(2)

                with r2c1:
                    if 'country' in col_map:
                        try:
                            country_counts = df[col_map['country']].value_counts().head(10).reset_index()
                            country_counts.columns = ['Country', 'Accidents']

                            fig_countries = px.bar(
                                country_counts.sort_values('Accidents'),
                                x='Accidents', y='Country', orientation='h',
                                color='Accidents',
                                color_continuous_scale=GREEN_SCALE
                            )
                            fig_countries.update_coloraxes(showscale=False)
                            hud_chart_layout(fig_countries, 350, "TOP 10 COUNTRIES")
                            st.plotly_chart(fig_countries, use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not generate country chart: {e}")

                with r2c2:
                    if 'aircraft' in col_map:
                        try:
                            ac_counts = df[col_map['aircraft']].value_counts().head(10).reset_index()
                            ac_counts.columns = ['Aircraft', 'Count']

                            fig_ac = px.bar(
                                ac_counts.sort_values('Count'),
                                x='Count', y='Aircraft', orientation='h',
                                color='Count',
                                color_continuous_scale=GREEN_SCALE
                            )
                            fig_ac.update_coloraxes(showscale=False)
                            hud_chart_layout(fig_ac, 350, "AIRCRAFT CATEGORIES")
                            st.plotly_chart(fig_ac, use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not generate aircraft chart: {e}")

                # Monthly heatmap
                if 'date' in col_map:
                    try:
                        hm_data = df.dropna(subset=['_year', '_month'])
                        if len(hm_data) > 0:
                            heatmap_df = hm_data.groupby(['_year', '_month']).size().reset_index(name='count')
                            heatmap_pivot = heatmap_df.pivot_table(
                                index='_month', columns='_year', values='count', fill_value=0
                            )
                            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                            y_labels = [month_names[int(m)-1] for m in heatmap_pivot.index
                                        if 1 <= int(m) <= 12]

                            fig_hm = go.Figure(data=go.Heatmap(
                                z=heatmap_pivot.values,
                                x=[str(int(c)) for c in heatmap_pivot.columns],
                                y=y_labels,
                                colorscale=HEATMAP_SCALE,
                                showscale=True,
                                colorbar=dict(
                                    title=dict(text="Count", font=dict(color=HUD_SUBTEXT)),
                                    tickfont=dict(color=HUD_SUBTEXT)
                                )
                            ))
                            hud_chart_layout(fig_hm, 380, "MONTHLY ACCIDENT HEATMAP")
                            st.plotly_chart(fig_hm, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not generate heatmap: {e}")

            # ─────────────────────────────────────
            #  TAB 2: RISK & SEVERITY ANALYSIS
            # ─────────────────────────────────────
            with tab2:

                r1c1, r1c2 = st.columns(2)

                # Severity donut chart
                with r1c1:
                    if 'severity' in col_map:
                        try:
                            sev_counts = df[col_map['severity']].value_counts().reset_index()
                            sev_counts.columns = ['Severity', 'Count']
                            sev_colors = [SEVERITY_COLORS.get(s, HUD_SECONDARY) for s in sev_counts['Severity']]

                            fig_sev = go.Figure(data=[go.Pie(
                                labels=sev_counts['Severity'],
                                values=sev_counts['Count'],
                                hole=0.5,
                                marker=dict(colors=sev_colors),
                                textfont=dict(color=HUD_TEXT)
                            )])
                            hud_chart_layout(fig_sev, 350, "FATALITY SEVERITY BREAKDOWN")
                            st.plotly_chart(fig_sev, use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not generate severity chart: {e}")

                # Fatality distribution pie
                with r1c2:
                    if 'fatalities' in col_map:
                        try:
                            fat_col = col_map['fatalities']
                            df['_fatal_bin'] = pd.cut(
                                df[fat_col].fillna(0),
                                bins=[-1, 0, 5, 20, float('inf')],
                                labels=['No Deaths', '1-5', '6-20', '20+']
                            )
                            fatal_dist = df['_fatal_bin'].value_counts().reset_index()
                            fatal_dist.columns = ['Category', 'Count']

                            fig_fdist = go.Figure(data=[go.Pie(
                                labels=fatal_dist['Category'],
                                values=fatal_dist['Count'],
                                hole=0.45,
                                marker=dict(colors=[HUD_PRIMARY, HUD_WARNING, "#ff6600", HUD_DANGER]),
                                textfont=dict(color=HUD_TEXT)
                            )])
                            hud_chart_layout(fig_fdist, 350, "FATALITY DISTRIBUTION")
                            st.plotly_chart(fig_fdist, use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not generate fatality distribution: {e}")

                # Top causes
                if 'cause' in col_map:
                    try:
                        cause_counts = df[col_map['cause']].value_counts().head(12).reset_index()
                        cause_counts.columns = ['Cause', 'Accidents']
                        cause_counts['Percentage'] = (cause_counts['Accidents'] / len(df) * 100).round(1)

                        fig_cause = px.bar(
                            cause_counts.sort_values('Accidents'),
                            x='Accidents', y='Cause', orientation='h',
                            color='Accidents',
                            color_continuous_scale=GREEN_SCALE,
                            text=cause_counts.sort_values('Accidents')['Percentage'].apply(
                                lambda x: f"{x:.1f}%")
                        )
                        fig_cause.update_traces(textposition='outside',
                                                textfont=dict(color=HUD_SUBTEXT, size=10))
                        fig_cause.update_coloraxes(showscale=False)
                        hud_chart_layout(fig_cause, 420, "TOP 12 ACCIDENT CAUSES")
                        st.plotly_chart(fig_cause, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not generate causes chart: {e}")

                # Severity by aircraft (stacked bar)
                r2c1, r2c2 = st.columns(2)

                with r2c1:
                    if 'severity' in col_map and 'aircraft' in col_map:
                        try:
                            cross = pd.crosstab(df[col_map['aircraft']], df[col_map['severity']])
                            top_ac = cross.sum(axis=1).nlargest(8).index
                            cross = cross.loc[top_ac]

                            fig_stack = go.Figure()
                            for sev_name in cross.columns:
                                fig_stack.add_trace(go.Bar(
                                    name=str(sev_name),
                                    y=cross.index.astype(str),
                                    x=cross[sev_name],
                                    orientation='h',
                                    marker_color=SEVERITY_COLORS.get(str(sev_name), HUD_SECONDARY)
                                ))
                            fig_stack.update_layout(barmode='stack')
                            hud_chart_layout(fig_stack, 350, "SEVERITY BY AIRCRAFT TYPE")
                            st.plotly_chart(fig_stack, use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not generate stacked chart: {e}")

                # Fatalities trend over years
                with r2c2:
                    if 'fatalities' in col_map and 'date' in col_map:
                        try:
                            fat_yearly = df.groupby('_year')[col_map['fatalities']].sum().reset_index()
                            fat_yearly.columns = ['Year', 'Fatalities']
                            fat_yearly = fat_yearly.dropna()

                            fig_fat_trend = go.Figure()
                            fig_fat_trend.add_trace(go.Scatter(
                                x=fat_yearly['Year'], y=fat_yearly['Fatalities'],
                                mode='lines+markers',
                                fill='tozeroy',
                                fillcolor='rgba(255,0,68,0.08)',
                                line=dict(color=HUD_DANGER, width=2),
                                marker=dict(size=6, color=HUD_DANGER),
                                name='Fatalities'
                            ))
                            hud_chart_layout(fig_fat_trend, 350, "FATALITIES TREND OVER YEARS")
                            st.plotly_chart(fig_fat_trend, use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not generate fatalities trend: {e}")

            # ─────────────────────────────────────
            #  TAB 3: DATA EXPLORER
            # ─────────────────────────────────────
            with tab3:

                # Filterable data table
                st.markdown(f"<p class='hud-section-title'>DATASET</p>", unsafe_allow_html=True)

                # Quick column filter
                display_cols = st.multiselect(
                    "Select columns to display",
                    options=df.columns.tolist(),
                    default=df.columns.tolist()[:12]
                )
                if display_cols:
                    st.dataframe(df[display_cols], use_container_width=True, height=400)
                else:
                    st.dataframe(df, use_container_width=True, height=400)

                # Download button
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "DOWNLOAD FILTERED DATA (CSV)",
                    data=csv_data,
                    file_name="filtered_aviation_data.csv",
                    mime="text/csv"
                )

                st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

                # Statistical summary
                stat_c1, stat_c2 = st.columns(2)

                with stat_c1:
                    st.markdown(f"<p class='hud-section-title'>NUMERIC SUMMARY</p>",
                                unsafe_allow_html=True)
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        num_summary = df[numeric_cols].describe().T[['mean', 'std', 'min', 'max']]
                        num_summary.columns = ['Mean', 'Std Dev', 'Min', 'Max']
                        st.dataframe(num_summary.round(2), use_container_width=True)
                    else:
                        st.markdown(f"<p style='color:{HUD_SUBTEXT};'>No numeric columns detected.</p>",
                                    unsafe_allow_html=True)

                with stat_c2:
                    st.markdown(f"<p class='hud-section-title'>CATEGORICAL SUMMARY</p>",
                                unsafe_allow_html=True)
                    cat_cols = df.select_dtypes(include=['object']).columns
                    if len(cat_cols) > 0:
                        cat_rows = []
                        for col in cat_cols[:8]:
                            mode_val = df[col].mode()
                            cat_rows.append({
                                'Column': col,
                                'Unique': df[col].nunique(),
                                'Most Common': mode_val.iloc[0] if len(mode_val) > 0 else 'N/A',
                                'Missing': df[col].isnull().sum()
                            })
                        st.dataframe(pd.DataFrame(cat_rows), use_container_width=True,
                                     hide_index=True)
                    else:
                        st.markdown(f"<p style='color:{HUD_SUBTEXT};'>No categorical columns detected.</p>",
                                    unsafe_allow_html=True)

                st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

                # Data quality report
                st.markdown(f"<p class='hud-section-title'>DATA QUALITY REPORT</p>",
                            unsafe_allow_html=True)

                total_missing = df.isnull().sum().sum()
                total_cells = df.shape[0] * df.shape[1]
                completeness = ((total_cells - total_missing) / total_cells * 100) if total_cells > 0 else 0
                duplicate_rows = df.duplicated().sum()
                date_range_txt = "N/A"
                if 'date' in col_map and '_year' in df.columns:
                    yr_min = df['_year'].dropna().min()
                    yr_max = df['_year'].dropna().max()
                    if not np.isnan(yr_min):
                        date_range_txt = f"{int(yr_min)} - {int(yr_max)}"

                qc1, qc2, qc3 = st.columns(3)
                with qc1:
                    st.markdown(hud_kpi_card("Data Completeness", f"{completeness:.1f}%",
                                             "secondary"), unsafe_allow_html=True)
                with qc2:
                    st.markdown(hud_kpi_card("Duplicate Rows", format_number(duplicate_rows),
                                             "warning" if duplicate_rows > 0 else ""),
                                unsafe_allow_html=True)
                with qc3:
                    st.markdown(hud_kpi_card("Date Range", date_range_txt, "secondary"),
                                unsafe_allow_html=True)

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

                # Missing values per column
                missing_df = pd.DataFrame({
                    'Column': df.columns,
                    'Missing': df.isnull().sum(),
                    'Percentage': (df.isnull().sum() / len(df) * 100).round(2)
                })
                missing_df = missing_df[missing_df['Missing'] > 0].sort_values('Missing', ascending=False)

                if len(missing_df) > 0:
                    st.markdown(f"""
                        <p style='color:{HUD_WARNING}; font-family:"Courier New",monospace;
                                  font-size:0.8rem;'>
                            COLUMNS WITH MISSING DATA
                        </p>
                    """, unsafe_allow_html=True)
                    st.dataframe(missing_df, use_container_width=True, hide_index=True)
                else:
                    st.markdown(f"""
                        <div style='background:{HUD_CARD_BG}; border:1px solid rgba(0,168,255,0.3);
                                    border-radius:8px; padding:12px; text-align:center;'>
                            <p style='color:{HUD_PRIMARY}; font-family:"Courier New",monospace;
                                      font-size:0.85rem; margin:0;'>
                                ALL CLEAR -- NO MISSING VALUES DETECTED
                            </p>
                        </div>
                    """, unsafe_allow_html=True)

    except Exception as e:
        st.markdown(f"""
            <div style='background:{HUD_CARD_BG}; border:1px solid rgba(255,0,68,0.4);
                        border-radius:8px; padding:16px; margin:12px 0;'>
                <p style='color:{HUD_DANGER}; font-family:"Courier New",monospace;
                          font-size:0.85rem; margin:0 0 8px 0;'>
                    ERROR: {str(e)}
                </p>
                <p style='color:{HUD_SUBTEXT}; font-size:0.8rem; margin:0;'>
                    Ensure the file is not corrupted and is a valid CSV or Excel file.
                    Try downloading the sample template above for reference.
                </p>
            </div>
        """, unsafe_allow_html=True)

else:
    # ═══════════════════════════════════════════════
    #  UPLOAD PLACEHOLDER (no file uploaded)
    # ═══════════════════════════════════════════════
    st.markdown(f"""
        <div style='background:{HUD_CARD_BG}; border-radius:12px; padding:48px 32px;
                    text-align:center; border:2px dashed {HUD_PRIMARY};
                    margin-top:20px; position:relative; overflow:hidden;'>
            <div style='width:80px; height:80px; margin:0 auto 20px auto;
                        border:2px solid {HUD_PRIMARY}; border-radius:50%;
                        display:flex; align-items:center; justify-content:center;
                        box-shadow:0 0 20px rgba(0,168,255,0.15);'>
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none"
                     stroke="{HUD_PRIMARY}" stroke-width="1.5">
                    <circle cx="12" cy="12" r="10" opacity="0.3"/>
                    <line x1="12" y1="2" x2="12" y2="22" opacity="0.15"/>
                    <line x1="2" y1="12" x2="22" y2="12" opacity="0.15"/>
                    <circle cx="12" cy="12" r="3"/>
                    <line x1="12" y1="8" x2="12" y2="3" stroke-width="2"/>
                </svg>
            </div>
            <p style='color:{HUD_PRIMARY}; font-family:"Courier New",monospace;
                      font-size:1.3rem; letter-spacing:3px; margin:0 0 8px 0;
                      text-shadow:0 0 10px rgba(0,168,255,0.3);'>
                AWAITING DATA UPLOAD
            </p>
            <p style='color:{HUD_SUBTEXT}; font-family:"Courier New",monospace;
                      font-size:0.8rem; letter-spacing:1px; margin:0;'>
                Drag and drop a CSV or Excel file above, or click to browse.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)

    # Feature cards
    st.markdown(f"<p class='hud-section-title'>DASHBOARD CAPABILITIES</p>",
                unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns(3)

    with fc1:
        st.markdown(f"""
            <div style='background:{HUD_CARD_BG}; border:1px solid {HUD_BORDER};
                        border-radius:8px; padding:24px; text-align:center;
                        min-height:180px;'>
                <div style='width:48px; height:48px; margin:0 auto 12px auto;
                            border:1px solid {HUD_PRIMARY}; border-radius:8px;
                            display:flex; align-items:center; justify-content:center;'>
                    <span style='color:{HUD_PRIMARY}; font-size:1.5rem;'>&#x2197;</span>
                </div>
                <p style='color:{HUD_PRIMARY}; font-family:"Courier New",monospace;
                          font-size:0.85rem; letter-spacing:1px; margin:0 0 8px 0;'>
                    TREND ANALYSIS
                </p>
                <p style='color:{HUD_SUBTEXT}; font-size:0.78rem; margin:0;
                          font-family:"Courier New",monospace;'>
                    Yearly trends, YoY changes, monthly heatmaps, geographic breakdown
                </p>
            </div>
        """, unsafe_allow_html=True)

    with fc2:
        st.markdown(f"""
            <div style='background:{HUD_CARD_BG}; border:1px solid {HUD_BORDER};
                        border-radius:8px; padding:24px; text-align:center;
                        min-height:180px;'>
                <div style='width:48px; height:48px; margin:0 auto 12px auto;
                            border:1px solid {HUD_WARNING}; border-radius:8px;
                            display:flex; align-items:center; justify-content:center;'>
                    <span style='color:{HUD_WARNING}; font-size:1.5rem;'>&#x26A0;</span>
                </div>
                <p style='color:{HUD_WARNING}; font-family:"Courier New",monospace;
                          font-size:0.85rem; letter-spacing:1px; margin:0 0 8px 0;'>
                    RISK & SEVERITY
                </p>
                <p style='color:{HUD_SUBTEXT}; font-size:0.78rem; margin:0;
                          font-family:"Courier New",monospace;'>
                    Severity donut, fatality distribution, cause analysis, stacked breakdowns
                </p>
            </div>
        """, unsafe_allow_html=True)

    with fc3:
        st.markdown(f"""
            <div style='background:{HUD_CARD_BG}; border:1px solid {HUD_BORDER};
                        border-radius:8px; padding:24px; text-align:center;
                        min-height:180px;'>
                <div style='width:48px; height:48px; margin:0 auto 12px auto;
                            border:1px solid {HUD_SECONDARY}; border-radius:8px;
                            display:flex; align-items:center; justify-content:center;'>
                    <span style='color:{HUD_SECONDARY}; font-size:1.5rem;'>&#x2630;</span>
                </div>
                <p style='color:{HUD_SECONDARY}; font-family:"Courier New",monospace;
                          font-size:0.85rem; letter-spacing:1px; margin:0 0 8px 0;'>
                    DATA EXPLORER
                </p>
                <p style='color:{HUD_SUBTEXT}; font-size:0.78rem; margin:0;
                          font-family:"Courier New",monospace;'>
                    Filterable tables, statistical summaries, data quality reports
                </p>
            </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════
st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)
st.markdown(f"""
    <div style='text-align:center; padding:16px 0; border-top:1px solid {HUD_BORDER};'>
        <p style='color:{HUD_PRIMARY}; font-family:"Courier New",monospace;
                  font-size:0.75rem; letter-spacing:2px; margin:0;
                  text-shadow:0 0 8px rgba(0,168,255,0.2);'>
            DYNAMIC ANALYSIS MODULE &mdash; AVIATION SAFETY INTELLIGENCE PLATFORM
        </p>
        <p style='color:{HUD_SUBTEXT}; font-family:"Courier New",monospace;
                  font-size:0.65rem; letter-spacing:1px; margin:4px 0 0 0;'>
            UPLOAD &bull; ANALYZE &bull; VISUALIZE
        </p>
    </div>
""", unsafe_allow_html=True)
