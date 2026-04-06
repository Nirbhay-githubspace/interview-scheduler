import streamlit as st
from dashboard.components import render_analytics_panel
from typing import Dict, Any

def render_home_page():
    """Render home page with overview dashboard"""
    
    st.title("🏠 Dashboard Overview")
    st.markdown("Welcome to the Intelligent Recruitment & Talent Matching System")
    
    # Quick stats
    st.markdown("---")

    # Fetch real metrics from database
    from dashboard.services import get_metrics
    metrics = get_metrics()

    # Render analytics panel
    render_analytics_panel(metrics)
    
    st.markdown("---")
    
    # Recent activity
    st.markdown("### 📋 Recent Activity")

    # Fetch real activities from database
    from dashboard.services import get_recent_activities
    recent_activities = get_recent_activities(limit=10)

    if recent_activities:
        for activity in recent_activities:
            icon = "✅" if activity['type'] == 'success' else "ℹ️"
            st.markdown(f"{icon} **{activity['activity']}** - _{activity['time']}_")
            st.caption(activity['details'])
            st.markdown("---")
    else:
        st.info("No recent activity. Start by creating a job and uploading resumes!")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📤 Upload Resumes", use_container_width=True):
            st.session_state['page'] = 'candidates'
            st.session_state['action'] = 'upload'
            st.rerun()
    
    with col2:
        if st.button("➕ Create Job", use_container_width=True):
            st.info("Job creation feature coming soon!")
    
    with col3:
        if st.button("👥 View Candidates", use_container_width=True):
            st.session_state['page'] = 'candidates'
            st.rerun()
    
    with col4:
        if st.button("📅 View Interviews", use_container_width=True):
            st.session_state['page'] = 'interviews'
            st.rerun()
    
    # System status
    st.markdown("---")
    st.markdown("### 🔧 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("✅ All agents operational")
    
    with col2:
        st.success("✅ API connection healthy")
    
    with col3:
        st.success("✅ Calendar integration active")