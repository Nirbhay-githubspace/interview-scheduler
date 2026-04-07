import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Any


def render_interviews_page():

    # =========================
    # GLOBAL HOME BUTTON (FIXED)
    # =========================
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.button("🏠 Home"):
            st.session_state["page"] = "Home"
            st.rerun()

    st.title("📅 Interviews")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 All Interviews", "🗓️ Calendar View", "➕ Schedule New"])

    with tab1:
        render_interviews_list()

    with tab2:
        render_calendar_view()

    with tab3:
        render_schedule_interface()


# =========================
# INTERVIEW LIST
# =========================
def render_interviews_list():

    st.markdown("### Scheduled Interviews")

    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Status",
            options=["All", "Scheduled", "Confirmed", "Completed", "Cancelled"]
        )

    with col2:
        date_filter = st.selectbox(
            "Time Period",
            options=["All Time", "Today", "This Week", "This Month", "Upcoming"]
        )

    with col3:
        candidate_search = st.text_input("🔍 Search candidate")

    from dashboard.services import get_interviews

    date_filter_map = {
        "Today": "today",
        "This Week": "this_week",
        "This Month": "this_month",
        "Upcoming": "upcoming"
    }

    interviews = get_interviews(
        status=status_filter.lower() if status_filter != "All" else None,
        date_filter=date_filter_map.get(date_filter)
    )

    if candidate_search:
        interviews = [
            i for i in interviews
            if candidate_search.lower() in i['candidate_name'].lower()
        ]

    st.markdown(f"**Showing {len(interviews)} interviews**")

    for interview in interviews:
        render_interview_card(interview)


# =========================
# INTERVIEW CARD
# =========================
def render_interview_card(interview: Dict[str, Any]):

    status_colors = {
        'scheduled': 'blue',
        'confirmed': 'green',
        'completed': 'gray',
        'cancelled': 'red'
    }

    status = interview['status'].lower()
    color = status_colors.get(status, 'blue')

    with st.container():
        st.markdown(f"""
        <div style="
            padding: 15px;
            border-left: 4px solid {color};
            background-color: #f8f9fa;
            border-radius: 5px;
            margin-bottom: 10px;
        "></div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            st.markdown(f"### 👤 {interview['candidate_name']}")
            st.caption(f"📧 {interview['candidate_email']}")
            st.caption(f"🎯 Score: {interview.get('overall_score', 'N/A')}%")

        with col2:
            st.write(f"📅 {interview['date']}")
            st.write(f"⏰ {interview['time']}")
            st.write(f"⏱ {interview['duration']} min")

            if interview.get('meeting_link'):
                st.link_button("Join Meeting", interview['meeting_link'])

        with col3:
            st.markdown(f"**{status.upper()}**")

            if status in ['scheduled', 'confirmed']:
                if st.button("✏️ Edit", key=f"edit_{interview['id']}"):
                    st.session_state['edit_interview'] = interview['id']
                    st.rerun()


# =========================
# CALENDAR VIEW
# =========================
def render_calendar_view():

    st.markdown("### Calendar View")

    selected_date = st.date_input("Select Date", value=datetime.now())

    from dashboard.services import get_interviews
    interviews = get_interviews()

    st.info(f"Showing calendar for {selected_date}")


# =========================
# SCHEDULE INTERVIEW
# =========================
def render_schedule_interface():

    st.markdown("### Schedule New Interview")

    from dashboard.services import get_candidates
    candidates = get_candidates()

    if not candidates:
        st.warning("No candidates available.")
        return

    selected_candidate = st.selectbox(
        "Candidate",
        options=[c['id'] for c in candidates],
        format_func=lambda x: next(c['name'] for c in candidates if c['id'] == x)
    )

    candidate = next(c for c in candidates if c['id'] == selected_candidate)

    interview_date = st.date_input("Date", value=datetime.now() + timedelta(days=1))
    interview_time = st.time_input("Time")
    duration = st.selectbox("Duration", [30, 45, 60])

    if st.button("Schedule Interview"):
        st.success(f"Interview scheduled for {candidate['name']}")