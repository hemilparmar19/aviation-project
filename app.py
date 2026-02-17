import streamlit as st
import os

st.set_page_config(
    page_title="Aviation Safety Intelligence",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Load CSS ────────────────────────────────────
def load_css():
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ── Sidebar Branding ────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 10px 0 20px 0;'>
            <h2 style='color:#4da6ff; margin:0;'>✈️</h2>
            <h3 style='color:#4da6ff; margin:4px 0 0 0;'>Aviation Safety</h3>
            <p style='color:#8899aa; font-size:0.8rem; margin:0;'>
                Intelligence Platform
            </p>
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

# ── Redirect to Home ────────────────────────────
st.switch_page("pages/1_Home.py")
