import streamlit as st
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(page_title="AI Risk Predictor | Aviation Safety",
                   page_icon="🤖", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

st.markdown("""
    <h1 style='color:#4da6ff;'>🤖 AI Risk Predictor</h1>
    <div style='background:#1a2035; padding:30px; border-radius:12px;
                border:1px solid #2a4a7f; text-align:center; margin-top:40px;'>
        <h2 style='color:#ffcc00;'>🚧 Coming on Day 2</h2>
        <p style='color:#8899aa; font-size:1.1rem;'>
            ML-powered accident risk prediction.<br>
            Select country, aircraft type and month to get your personalized risk score.
        </p>
    </div>
""", unsafe_allow_html=True)
