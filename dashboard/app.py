"""
Main Streamlit Dashboard Application
"""

import streamlit as st
import sys
from pathlib import Path

# =========================
# PATH SETUP
# =========================
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# =========================
# IMPORT PAGES
# =========================
from dashboard.views import (
    render_home_page,
    render_candidates_page,
    render_interviews_page
)
from dashboard.views.jobs import render_jobs_page

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Intelligent Recruitment System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# SESSION STATE (CLEAN INIT)
# =========================
if "user" not in st.session_state:
    st.session_state.user = {
        "name": "Admin User",
        "email": "admin@recruitment.ai",
        "role": "Recruiter"
    }

# 🔥 IMPORTANT: CLEAN DEFAULT STATE
if "candidates" not in st.session_state:
    st.session_state["candidates"] = []

if "selected_job" not in st.session_state:
    st.session_state["selected_job"] = None

# 🔥 NAVIGATION STATE (FIX BUTTON NAVIGATION)
if "page" not in st.session_state:
    st.session_state["page"] = "Home"

# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.markdown("## 🤖 Recruitment AI")
    st.caption("Intelligent Hiring System")

    st.divider()

    # 🔥 RADIO SYNCED WITH SESSION STATE
    page = st.radio(
        "Navigation",
        ["Home", "Jobs", "Candidates", "Interviews"],
        index=["Home", "Jobs", "Candidates", "Interviews"].index(st.session_state["page"])
    )

    # 🔥 KEEP PAGE STATE IN SYNC
    st.session_state["page"] = page

    st.divider()

    st.markdown(f"👤 **{st.session_state.user['name']}**")
    st.caption(st.session_state.user['email'])

# =========================
# ROUTING (STABLE)
# =========================
page = st.session_state["page"]

if page == "Home":
    render_home_page()

elif page == "Jobs":
    render_jobs_page()

elif page == "Candidates":
    render_candidates_page()

elif page == "Interviews":
    render_interviews_page()