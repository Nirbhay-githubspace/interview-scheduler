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
# SESSION STATE
# =========================
if "user" not in st.session_state:
    st.session_state.user = {
        "name": "Admin User",
        "email": "admin@recruitment.ai",
        "role": "Recruiter"
    }

if "candidates" not in st.session_state:
    st.session_state["candidates"] = []

if "selected_job" not in st.session_state:
    st.session_state["selected_job"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "Home"

# =========================
# SIDEBAR (SYNCED)
# =========================
with st.sidebar:

    st.markdown("## 🤖 Recruitment AI")
    st.caption("Intelligent Hiring System")

    st.divider()

    pages = ["Home", "Jobs", "Candidates", "Interviews"]

    selected_page = st.radio(
        "Navigation",
        pages,
        index=pages.index(st.session_state["page"]),
        key="sidebar_nav"
    )

    if selected_page != st.session_state["page"]:
        st.session_state["page"] = selected_page
        st.rerun()

    st.divider()

    st.markdown(f"👤 **{st.session_state.user['name']}**")
    st.caption(st.session_state.user['email'])

# =========================
# ROUTING
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