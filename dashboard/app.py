"""
Main Streamlit Dashboard Application
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import pages
from dashboard.pages import render_home_page, render_candidates_page, render_interviews_page
from dashboard.pages.jobs import render_jobs_page

# Page config
st.set_page_config(
    page_title="Intelligent Recruitment System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# SESSION STATE
# =========================
if 'user' not in st.session_state:
    st.session_state.user = {
        'name': 'Admin User',
        'email': 'admin@recruitment.ai',
        'role': 'Recruiter'
    }

# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.markdown("## 🤖 Recruitment AI")
    st.caption("Intelligent Hiring System")

    st.divider()

    # 🔥 CLEAN NAVIGATION (NO EMOJIS = NO BUGS)
    page = st.radio(
        "Navigation",
        ["Home", "Jobs", "Candidates", "Interviews"]
    )

    st.divider()

    st.markdown(f"👤 **{st.session_state.user['name']}**")
    st.caption(st.session_state.user['email'])

# =========================
# ROUTING (FIXED)
# =========================

if page == "Home":
    render_home_page()

elif page == "Jobs":
    render_jobs_page()

elif page == "Candidates":
    render_candidates_page()

elif page == "Interviews":
    render_interviews_page()