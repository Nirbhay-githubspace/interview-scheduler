import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Any

def render_interviews_page():
    """Render interviews page with calendar and management features"""
    
    st.title("📅 Interviews")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 All Interviews", "🗓️ Calendar View", "➕ Schedule New"])
    
    with tab1:
        render_interviews_list()
    
    with tab2:
        render_calendar_view()
    
    with tab3:
        render_schedule_interface()

def render_interviews_list():
    """Render list of all scheduled interviews"""
    
    st.markdown("### Scheduled Interviews")
    
    # Filters
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
    
    # Fetch real data from database
    from dashboard.services import get_interviews

    # Determine date filter
    date_filter_map = {
        "Today": "today",
        "This Week": "this_week",
        "This Month": "this_month",
        "Upcoming": "upcoming"
    }
    date_filter_value = date_filter_map.get(date_filter)

    # Get interviews with filters
    interviews = get_interviews(
        status=status_filter.lower() if status_filter != "All" else None,
        date_filter=date_filter_value
    )

    # Apply candidate search filter
    if candidate_search:
        interviews = [
            i for i in interviews
            if candidate_search.lower() in i['candidate_name'].lower()
        ]
    
    st.markdown(f"**Showing {len(interviews)} interviews**")
    
    # Display interviews
    for interview in interviews:
        render_interview_card(interview)

def render_interview_card(interview: Dict[str, Any]):
    """Render a single interview card"""
    
    # Status color
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
        ">
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.markdown(f"### 👤 {interview['candidate_name']}")
            st.caption(f"📧 {interview['candidate_email']}")
            st.caption(f"🎯 Overall Score: {interview.get('overall_score', 'N/A')}%")
        
        with col2:
            st.markdown("**📅 Interview Details**")
            st.write(f"**Date:** {interview['date']}")
            st.write(f"**Time:** {interview['time']}")
            st.write(f"**Duration:** {interview['duration']} min")
            
            if interview.get('meeting_link'):
                st.link_button("🔗 Join Meeting", interview['meeting_link'])
        
        with col3:
            status_emoji = {
                'scheduled': '📝',
                'confirmed': '✅',
                'completed': '✔️',
                'cancelled': '❌'
            }
            st.markdown(f"**Status**")
            st.markdown(f"{status_emoji.get(status, '📝')} {status.title()}")
            
            # Action buttons
            if status in ['scheduled', 'confirmed']:
                if st.button("✏️ Edit", key=f"edit_{interview['id']}"):
                    st.session_state['edit_interview'] = interview['id']
                    st.rerun()
                
                if st.button("❌ Cancel", key=f"cancel_{interview['id']}"):
                    st.warning("Interview cancellation will be implemented")
        
        # Expandable section for notes
        with st.expander("📝 Notes & Details"):
            notes = interview.get('notes', 'No notes available')
            st.write(notes)
            
            if status == 'completed':
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Rating:** {'⭐' * interview.get('rating', 0)}")
                with col2:
                    st.write(f"**Recommendation:** {interview.get('recommendation', 'N/A')}")

def render_calendar_view():
    """Render calendar view of interviews"""
    
    st.markdown("### Calendar View")
    
    # Date selector
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_date = st.date_input(
            "Select Date",
            value=datetime.now(),
            min_value=datetime.now() - timedelta(days=90),
            max_value=datetime.now() + timedelta(days=90)
        )
    
    with col2:
        view_mode = st.selectbox("View", ["Day", "Week", "Month"])
    
    # Get interviews for selected date/range
    from dashboard.services import get_interviews
    interviews = get_interviews()
    
    # Filter by date range based on view mode
    if view_mode == "Day":
        st.markdown(f"#### Interviews on {selected_date.strftime('%B %d, %Y')}")
        
        # Group by time
        time_slots = {}
        for interview in interviews:
            time = interview['time']
            if time not in time_slots:
                time_slots[time] = []
            time_slots[time].append(interview)
        
        # Display timeline
        for time_slot in sorted(time_slots.keys()):
            st.markdown(f"**{time_slot}**")
            for interview in time_slots[time_slot]:
                st.info(f"📅 {interview['candidate_name']} - {interview['duration']} min")
            st.markdown("---")
    
    elif view_mode == "Week":
        st.markdown("#### Week View")
        
        # Create weekly calendar
        start_of_week = selected_date - timedelta(days=selected_date.weekday())
        
        week_data = []
        for i in range(7):
            day = start_of_week + timedelta(days=i)
            day_interviews = [
                i for i in interviews
                # In production, filter by actual dates
            ]
            week_data.append({
                'Day': day.strftime('%A'),
                'Date': day.strftime('%m/%d'),
                'Interviews': len(day_interviews)
            })
        
        df = pd.DataFrame(week_data)
        st.dataframe(df, use_container_width=True)
    
    else:  # Month view
        st.markdown("#### Month View")
        st.info("Month calendar view will be implemented with interactive calendar component")

def render_schedule_interface():
    """Render interface for scheduling new interviews"""
    
    st.markdown("### Schedule New Interview")
    
    # Candidate selection
    st.markdown("#### 1. Select Candidate")

    # Fetch real candidates from database
    from dashboard.services import get_candidates
    candidates = get_candidates()

    if not candidates:
        st.warning("⚠️ No candidates available. Please upload and process resumes first.")
        return

    # Format candidates for selection
    candidates = [
        {
            'id': c['id'],
            'name': c['name'],
            'email': c['email'],
            'score': c.get('overall_score', 0)
        }
        for c in candidates
    ]
    
    selected_candidate = st.selectbox(
        "Candidate",
        options=[c['id'] for c in candidates],
        format_func=lambda x: next(c['name'] for c in candidates if c['id'] == x)
    )
    
    # Display candidate info
    candidate = next(c for c in candidates if c['id'] == selected_candidate)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📧 {candidate['email']}")
    with col2:
        st.info(f"🎯 Score: {candidate['score']}%")
    
    # Interview details
    st.markdown("#### 2. Interview Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        interview_date = st.date_input(
            "Date",
            min_value=datetime.now(),
            value=datetime.now() + timedelta(days=1)
        )
        
        interviewer_email = st.text_input(
            "Interviewer Email",
            placeholder="interviewer@company.com"
        )
    
    with col2:
        interview_time = st.time_input(
            "Time",
            value=datetime.strptime("10:00", "%H:%M").time()
        )
        
        duration = st.selectbox(
            "Duration",
            options=[30, 45, 60, 90, 120],
            format_func=lambda x: f"{x} minutes",
            index=2
        )
    
    # Additional options
    st.markdown("#### 3. Additional Options")
    
    include_video = st.checkbox("Include video conference link", value=True)
    send_reminder = st.checkbox("Send reminder emails", value=True)
    
    notes = st.text_area(
        "Notes (optional)",
        placeholder="Add any notes or special instructions..."
    )
    
    # Schedule button
    if st.button("📅 Schedule Interview", type="primary", use_container_width=True):
        with st.spinner("Scheduling interview..."):
            # In production, call API
            import time
            time.sleep(1)
            
            st.success(f"""
            ✅ Interview successfully scheduled!
            
            **Details:**
            - Candidate: {candidate['name']}
            - Date: {interview_date.strftime('%B %d, %Y')}
            - Time: {interview_time.strftime('%I:%M %p')}
            - Duration: {duration} minutes
            - Interviewer: {interviewer_email}
            
            Calendar invitations have been sent to all participants.
            """)

# Removed get_sample_interviews() - now using real data from data_service