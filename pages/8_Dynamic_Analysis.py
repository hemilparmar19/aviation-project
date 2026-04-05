import streamlit as st
import pandas as pd
import numpy as np
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.helpers import format_number
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dynamic Analysis | Aviation Safety",
                   page_icon="📤", layout="wide")

def load_css():
    css_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "style.css"))
    if os.path.exists(css_path):
         with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

DARK = dict(plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
            font=dict(color="#ffffff"),
            margin=dict(l=20,r=20,t=40,b=20))

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

# ═══════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════
st.markdown("<h1 style='color:#4da6ff;'>📤 Dynamic Analysis</h1>", unsafe_allow_html=True)
st.markdown("""
    <p style='color:#8899aa;'>
        Upload your own aviation accident dataset (CSV or Excel) and instantly generate
        interactive charts and insights. This page operates independently and won't affect other pages.
    </p>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  DOWNLOAD TEMPLATE
# ═══════════════════════════════════════════════
col_info, col_template = st.columns([2, 1])

with col_info:
    st.info("""
        **📋 Expected Columns (flexible naming):**
        - Date column (e.g., `acc._date`, `date`, `accident_date`)
        - Country column (e.g., `country`, `country_clean`, `nation`)
        - Fatalities column (e.g., `fat.`, `fatalities`, `deaths`)
        - Severity column (e.g., `Fatality_Severity`, `severity`)
        - Aircraft type (e.g., `aircraft_category`, `aircraft`)
        - Cause/Reason (e.g., `reason_clean`, `cause`)
    """)

with col_template:
    st.markdown("<br>", unsafe_allow_html=True)
    template_df = generate_template()
    st.download_button(
        "📥 Download Sample Template",
        data=template_df.to_csv(index=False),
        file_name="aviation_accident_template.csv",
        mime="text/csv",
        use_container_width=True
    )

st.divider()

# ═══════════════════════════════════════════════
#  FILE UPLOAD
# ═══════════════════════════════════════════════
st.subheader("📂 Upload Your Dataset")

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=['csv', 'xlsx', 'xls'],
    help="Upload aviation accident data in CSV or Excel format"
)

if uploaded_file is not None:
    try:
        # Read file based on extension
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ File uploaded successfully: **{uploaded_file.name}**")
        
        # ── Data Preview ─────────────────────────
        st.subheader("📊 Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
        # ── Summary Statistics ───────────────────
        st.subheader("📈 Dataset Summary")
        sum1, sum2, sum3, sum4 = st.columns(4)
        with sum1:
            st.metric("📋 Total Records", format_number(len(df)))
        with sum2:
            st.metric("📊 Total Columns", len(df.columns))
        with sum3:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            st.metric("🔢 Numeric Columns", len(numeric_cols))
        with sum4:
            st.metric("💾 File Size", f"{uploaded_file.size / 1024:.1f} KB")
        
        st.divider()
        
        # ── Column Mapping ───────────────────────
        st.subheader("🔍 Auto-Detected Columns")
        col_map = smart_column_mapper(df)
        
        if not col_map:
            st.warning("⚠️ Could not auto-detect standard columns. Please ensure your data has columns for date, country, fatalities, etc.")
            st.info("💡 **Tip:** Download the sample template above to see the expected format.")
        else:
            # Show detected mappings
            map_cols = st.columns(len(col_map))
            for i, (field, col_name) in enumerate(col_map.items()):
                with map_cols[i]:
                    st.markdown(f"""
                        <div style='background:#1a2035;padding:12px;border-radius:8px;
                                    border-left:3px solid #4da6ff;text-align:center;'>
                            <p style='color:#8899aa;margin:0;font-size:0.75rem;'>{field.upper()}</p>
                            <p style='color:#4da6ff;margin:0;font-weight:600;'>{col_name}</p>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.divider()
            
            # ═══════════════════════════════════════
            #  GENERATE CHARTS
            # ═══════════════════════════════════════
            st.subheader("📊 Auto-Generated Insights")
            
            # ── Chart 1: Yearly Trend ────────────
            if 'date' in col_map:
                try:
                    df[col_map['date']] = pd.to_datetime(df[col_map['date']], errors='coerce')
                    df['year'] = df[col_map['date']].dt.year
                    yearly = df.groupby('year').size().reset_index(name='accidents')
                    
                    fig1 = go.Figure()
                    fig1.add_trace(go.Scatter(
                        x=yearly['year'], y=yearly['accidents'],
                        mode='lines+markers',
                        line=dict(color='#4da6ff', width=3),
                        marker=dict(size=8, color='#4da6ff'),
                        fill='tozeroy',
                        fillcolor='rgba(77,166,255,0.1)',
                        name='Accidents'
                    ))
                    fig1.update_layout(
                        **DARK,
                        title="📈 Yearly Accident Trend",
                        xaxis=dict(title="Year", gridcolor="#1a2035"),
                        yaxis=dict(title="Number of Accidents", gridcolor="#1a2035"),
                        height=350
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not generate yearly trend: {e}")
            
            # ── Charts Row 2 ──────────────────────
            chart_col1, chart_col2 = st.columns(2)
            
            # Chart 2: Top Countries
            with chart_col1:
                if 'country' in col_map:
                    try:
                        country_counts = df[col_map['country']].value_counts().head(10).reset_index()
                        country_counts.columns = ['Country', 'Accidents']
                        
                        fig2 = px.bar(
                            country_counts.sort_values('Accidents'),
                            x='Accidents', y='Country', orientation='h',
                            color='Accidents',
                            color_continuous_scale=[[0,'#1a3a6f'],[1,'#4da6ff']],
                            title="🌍 Top 10 Countries by Accidents"
                        )
                        fig2.update_coloraxes(showscale=False)
                        fig2.update_layout(**DARK, height=350)
                        st.plotly_chart(fig2, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not generate country chart: {e}")
            
            # Chart 3: Fatality Distribution
            with chart_col2:
                if 'fatalities' in col_map:
                    try:
                        df['fatal_category'] = pd.cut(
                            df[col_map['fatalities']],
                            bins=[-1, 0, 5, 20, 1000],
                            labels=['No Deaths', '1-5 Deaths', '6-20 Deaths', '20+ Deaths']
                        )
                        fatal_dist = df['fatal_category'].value_counts().reset_index()
                        fatal_dist.columns = ['Category', 'Count']
                        
                        fig3 = px.pie(
                            fatal_dist,
                            values='Count', names='Category',
                            hole=0.4,
                            title="💀 Fatality Distribution",
                            color_discrete_sequence=['#00ff88','#ffcc00','#ff6600','#ff0044']
                        )
                        fig3.update_layout(**DARK, height=350)
                        st.plotly_chart(fig3, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not generate fatality chart: {e}")
            
            # ── Charts Row 3 ──────────────────────
            chart_col3, chart_col4 = st.columns(2)
            
            # Chart 4: Severity Breakdown
            with chart_col3:
                if 'severity' in col_map:
                    try:
                        sev_counts = df[col_map['severity']].value_counts().reset_index()
                        sev_counts.columns = ['Severity', 'Count']
                        
                        color_map = {
                            'Non-Fatal': '#00ff88',
                            'Low': '#ffcc00',
                            'Medium': '#ff6600',
                            'High': '#ff0044'
                        }
                        sev_counts['Color'] = sev_counts['Severity'].map(
                            lambda x: color_map.get(x, '#4da6ff')
                        )
                        
                        fig4 = go.Figure(data=[go.Bar(
                            x=sev_counts['Severity'],
                            y=sev_counts['Count'],
                            marker_color=sev_counts['Color']
                        )])
                        fig4.update_layout(
                            **DARK,
                            title="⚡ Accidents by Severity",
                            xaxis=dict(title="Severity", gridcolor="#1a2035"),
                            yaxis=dict(title="Count", gridcolor="#1a2035"),
                            height=350
                        )
                        st.plotly_chart(fig4, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not generate severity chart: {e}")
            
            # Chart 5: Aircraft Category
            with chart_col4:
                if 'aircraft' in col_map:
                    try:
                        aircraft_counts = df[col_map['aircraft']].value_counts().head(8).reset_index()
                        aircraft_counts.columns = ['Aircraft Type', 'Count']
                        
                        fig5 = px.bar(
                            aircraft_counts.sort_values('Count'),
                            x='Count', y='Aircraft Type', orientation='h',
                            title="✈️ Top Aircraft Categories"
                        )
                        fig5.update_traces(marker_color='#4da6ff')
                        fig5.update_layout(**DARK, height=350)
                        st.plotly_chart(fig5, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not generate aircraft chart: {e}")
            
            # ── Chart 6: Top Causes (Full Width) ─
            if 'cause' in col_map:
                try:
                    st.markdown("#### 🔥 Top Accident Causes")
                    cause_counts = df[col_map['cause']].value_counts().head(12).reset_index()
                    cause_counts.columns = ['Cause', 'Accidents']
                    cause_counts['Percentage'] = (cause_counts['Accidents'] / len(df) * 100).round(1)
                    
                    fig6 = px.bar(
                        cause_counts.sort_values('Accidents'),
                        x='Accidents', y='Cause', orientation='h',
                        color='Percentage',
                        color_continuous_scale=[[0,'#1a3a6f'],[1,'#ff6600']],
                        title="Primary Causes of Accidents",
                        hover_data={'Percentage': ':.1f'}
                    )
                    fig6.update_coloraxes(showscale=True, colorbar_title="% of Total")
                    fig6.update_layout(**DARK, height=420)
                    st.plotly_chart(fig6, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not generate causes chart: {e}")
            
            st.divider()
            
            # ═══════════════════════════════════════
            #  STATISTICAL SUMMARY
            # ═══════════════════════════════════════
            st.subheader("📊 Statistical Summary")
            
            stat_col1, stat_col2 = st.columns(2)
            
            with stat_col1:
                st.markdown("**Numeric Columns Summary:**")
                numeric_summary = df.select_dtypes(include=[np.number]).describe().T
                numeric_summary = numeric_summary[['mean', 'std', 'min', 'max']]
                numeric_summary.columns = ['Mean', 'Std Dev', 'Min', 'Max']
                st.dataframe(numeric_summary.round(2), use_container_width=True)
            
            with stat_col2:
                st.markdown("**Categorical Columns Summary:**")
                cat_cols = df.select_dtypes(include=['object']).columns
                cat_summary = []
                for col in cat_cols[:5]:  # Show first 5 categorical columns
                    cat_summary.append({
                        'Column': col,
                        'Unique Values': df[col].nunique(),
                        'Most Common': df[col].mode()[0] if len(df[col].mode()) > 0 else 'N/A',
                        'Missing': df[col].isnull().sum()
                    })
                if cat_summary:
                    st.dataframe(pd.DataFrame(cat_summary), use_container_width=True, hide_index=True)
            
            st.divider()
            
            # ═══════════════════════════════════════
            #  DATA QUALITY REPORT
            # ═══════════════════════════════════════
            st.subheader("✅ Data Quality Report")
            
            quality_col1, quality_col2, quality_col3 = st.columns(3)
            
            with quality_col1:
                total_missing = df.isnull().sum().sum()
                total_cells = df.shape[0] * df.shape[1]
                completeness = ((total_cells - total_missing) / total_cells * 100)
                st.metric("Data Completeness", f"{completeness:.1f}%")
            
            with quality_col2:
                duplicate_rows = df.duplicated().sum()
                st.metric("Duplicate Rows", format_number(duplicate_rows))
            
            with quality_col3:
                if 'date' in col_map:
                    date_range = f"{df['year'].min()}-{df['year'].max()}"
                else:
                    date_range = "N/A"
                st.metric("Date Range", date_range)
            
            # Missing values per column
            missing_df = pd.DataFrame({
                'Column': df.columns,
                'Missing Values': df.isnull().sum(),
                'Percentage': (df.isnull().sum() / len(df) * 100).round(2)
            })
            missing_df = missing_df[missing_df['Missing Values'] > 0].sort_values('Missing Values', ascending=False)
            
            if len(missing_df) > 0:
                st.markdown("**Columns with Missing Data:**")
                st.dataframe(missing_df, use_container_width=True, hide_index=True)
            else:
                st.success("✅ No missing values detected in the dataset!")
            
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        st.info("💡 **Troubleshooting:**\n- Ensure the file is not corrupted\n- Check that it's a valid CSV or Excel file\n- Try downloading and using the sample template above")

else:
    # ── Show instructions when no file uploaded ─
    st.markdown("""
        <div style='background:#1a2035;border-radius:14px;padding:40px;
                    text-align:center;border:2px dashed #2a4a7f;margin-top:20px;'>
            <div style='font-size:4rem;'>📤</div>
            <h3 style='color:#4da6ff;'>Upload Your Dataset to Begin</h3>
            <p style='color:#8899aa;'>
                Drag and drop a CSV or Excel file above, or click to browse.<br>
                Your data will be analyzed and visualized instantly.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Show example of what charts will be generated
    st.divider()
    st.subheader("📊 What You'll Get After Upload")
    
    ex1, ex2, ex3 = st.columns(3)
    with ex1:
        st.markdown("""
            <div class='nav-card'>
                <div style='font-size:2rem;'>📈</div>
                <h4>Trend Analysis</h4>
                <p>Yearly accident trends with interactive line charts</p>
            </div>
        """, unsafe_allow_html=True)
    
    with ex2:
        st.markdown("""
            <div class='nav-card'>
                <div style='font-size:2rem;'>🌍</div>
                <h4>Geographic Insights</h4>
                <p>Top countries by accident frequency</p>
            </div>
        """, unsafe_allow_html=True)
    
    with ex3:
        st.markdown("""
            <div class='nav-card'>
                <div style='font-size:2rem;'>⚡</div>
                <h4>Severity Analysis</h4>
                <p>Breakdown by fatality levels and damage</p>
            </div>
        """, unsafe_allow_html=True)

st.divider()
st.markdown("<div class='footer'>📤 Dynamic Analysis | Upload & Visualize Your Data | Aviation Safety Intelligence Platform</div>",
            unsafe_allow_html=True)
