import streamlit as st
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(page_title="Accident Explorer | Aviation Safety",
                   page_icon="🔍", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

st.markdown("""
    <h1 style='color:#4da6ff;'>🔍 Accident Explorer</h1>
    <div style='background:#1a2035; padding:30px; border-radius:12px;
                border:1px solid #2a4a7f; text-align:center; margin-top:40px;'>
        <h2 style='color:#ffcc00;'>🚧 Coming on Day 2</h2>
        <p style='color:#8899aa; font-size:1.1rem;'>
            Search, filter and explore all 2,596 accidents.<br>
            Click any accident for full details and similar cases.
        </p>
    </div>
""", unsafe_allow_html=True)
