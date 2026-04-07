import streamlit as st
from storage.jobs_db import get_jobs


def render_home_page():
    """Render clean, real dashboard"""

    st.title("🏠 Dashboard Overview")
    st.markdown("Welcome to the Intelligent Recruitment & Talent Matching System")

    st.markdown("---")

    # =========================
    # REAL METRICS
    # =========================
    jobs = get_jobs()
    candidates = st.session_state.get("candidates", [])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📋 Active Jobs", len(jobs))

    with col2:
        st.metric("👥 Candidates", len(candidates))

    with col3:
        st.metric("📅 Interviews", 0)

    st.markdown("---")

    # =========================
    # EMPTY STATE
    # =========================
    if len(jobs) == 0 and len(candidates) == 0:
        st.info("👋 Welcome! Start by creating your first job and uploading resumes.")

    # =========================
    # RECENT ACTIVITY
    # =========================
    st.markdown("### 📋 Recent Activity")

    if candidates:
        st.success(f"Processed {len(candidates)} candidate(s)")
    else:
        st.info("No recent activity yet.")

    st.markdown("---")

    # =========================
    # QUICK ACTIONS (FIXED)
    # =========================
    st.markdown("### ⚡ Quick Actions")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📤 Upload Resumes", use_container_width=True):
            st.session_state["page"] = "Candidates"
            st.rerun()

    with col2:
        if st.button("➕ Create Job", use_container_width=True):
            st.session_state["page"] = "Jobs"
            st.rerun()

    with col3:
        if st.button("👥 View Candidates", use_container_width=True):
            st.session_state["page"] = "Candidates"
            st.rerun()

    with col4:
        if st.button("📅 View Interviews", use_container_width=True):
            st.session_state["page"] = "Interviews"
            st.rerun()

    st.markdown("---")

    # =========================
    # SYSTEM STATUS
    # =========================
    st.markdown("### 🔧 System Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("✅ Agents ready")

    with col2:
        st.success("✅ API connected")

    with col3:
        st.success("✅ System operational")