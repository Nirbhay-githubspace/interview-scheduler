

import streamlit as st
from storage.jobs_db import get_jobs

def render_home_page():
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.button("🏠 Home"):
            st.session_state["page"] = "Home"
        st.rerun()

    # 🔥 GLOBAL HOME BUTTON (kept for consistency)
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.button("🏠 Home"):
            st.session_state["page"] = "Home"
            st.rerun()

    st.title("🏠 Dashboard Overview")
    st.markdown("Welcome to the Intelligent Recruitment & Talent Matching System")

    st.markdown("---")

    jobs = get_jobs()
    candidates = st.session_state.get("candidates", [])

    col1, col2, col3 = st.columns(3)

    col1.metric("📋 Active Jobs", len(jobs))
    col2.metric("👥 Candidates", len(candidates))
    col3.metric("📅 Interviews", 0)

    st.markdown("---")

    if len(jobs) == 0 and len(candidates) == 0:
        st.info("👋 Welcome! Start by creating your first job and uploading resumes.")

    st.markdown("### ⚡ Quick Actions")

    col1, col2, col3, col4 = st.columns(4)

    if col1.button("📤 Upload Resumes"):
        st.session_state["page"] = "Candidates"
        st.rerun()

    if col2.button("➕ Create Job"):
        st.session_state["page"] = "Jobs"
        st.rerun()

    if col3.button("👥 View Candidates"):
        st.session_state["page"] = "Candidates"
        st.rerun()

    if col4.button("📅 View Interviews"):
        st.session_state["page"] = "Interviews"
        st.rerun()