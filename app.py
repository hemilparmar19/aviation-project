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
         with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ── Sidebar Branding ────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 10px 0 20px 0;'>
            <div style='font-size:2.2rem; margin-bottom:4px;'>&#9992;</div>
            <h3 style='color:#00a8ff; margin:4px 0 0 0; font-family:"Share Tech Mono",monospace;
                        text-shadow:0 0 10px rgba(0,168,255,0.4);'>AVIATION SAFETY</h3>
            <p style='color:#7a8a9a; font-size:0.75rem; margin:0;
                       letter-spacing:3px; text-transform:uppercase;'>
                Intelligence Platform
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
        <div style='color:#7a8a9a; font-size:0.8rem; line-height:2;
                    font-family:"Share Tech Mono",monospace;'>
            <span style='color:#00a8ff;'>></span> <b style='color:#e0e0e0;'>DATASET:</b> 2015-2025<br>
            <span style='color:#00a8ff;'>></span> <b style='color:#e0e0e0;'>COVERAGE:</b> GLOBAL<br>
            <span style='color:#00a8ff;'>></span> <b style='color:#e0e0e0;'>RECORDS:</b> 2,596<br>
            <span style='color:#00a8ff;'>></span> <b style='color:#e0e0e0;'>TABLES:</b> 4 (JOINED)<br>
        </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
        <div style='color:#7a8a9a; font-size:0.75rem; text-align:center;
                    font-family:"Share Tech Mono",monospace;'>
            THIRD YEAR DATA SCIENCE PROJECT<br>
            <b style='color:#00d4ff;'>TREND ANALYSIS OF GLOBAL<br>AIRPLANE ACCIDENTS</b>
        </div>
    """, unsafe_allow_html=True)

# ── Redirect to Home ────────────────────────────
st.switch_page("pages/1_Home.py")
