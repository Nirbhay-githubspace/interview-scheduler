"""
Jobs page for managing job descriptions
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime

def render_jobs_page():
    """Render jobs management page"""
    
    st.title("📋 Job Descriptions")
    
    tabs = st.tabs(["Active Jobs", "Create New Job", "View Job Details"])
    
    # Tab 1: Active Jobs
    with tabs[0]:
        render_active_jobs()
    
    # Tab 2: Create New Job
    with tabs[1]:
        render_create_job()
    
    # Tab 3: View Details
    with tabs[2]:
        render_job_details()


def render_create_job():
    """Form to create a new job description"""
    
    st.subheader("Create New Job Description")
    
    with st.form("create_job_form"):
        # Basic Information
        st.markdown("### 📝 Basic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            job_id = st.text_input(
                "Job ID*",
                placeholder="e.g., job_001, eng_senior_2024",
                help="Unique identifier for this job"
            )
            
            title = st.text_input(
                "Job Title*",
                placeholder="e.g., Senior Software Engineer"
            )
            
            department = st.text_input(
                "Department",
                placeholder="e.g., Engineering"
            )
        
        with col2:
            location = st.text_input(
                "Location*",
                placeholder="e.g., San Francisco, CA"
            )
            
            work_location_type = st.selectbox(
                "Work Location Type",
                ["Hybrid", "Remote", "On-site"]
            )
            
            experience_level = st.selectbox(
                "Experience Level*",
                ["Entry", "Junior", "Mid", "Senior", "Lead", "Principal"]
            )
        
        # Job Description
        st.markdown("### 📄 Description")
        
        description = st.text_area(
            "Job Description*",
            placeholder="Provide a detailed description of the role...",
            height=150
        )
        
        # Responsibilities
        st.markdown("### ✅ Responsibilities")
        responsibilities_text = st.text_area(
            "Enter responsibilities (one per line)",
            placeholder="Design and develop scalable applications\nLead technical discussions\nMentor junior developers",
            height=100
        )
        
        # Required Skills
        st.markdown("### 🎯 Required Skills")
        
        col1, col2 = st.columns(2)
        
        with col1:
            required_skills_text = st.text_area(
                "Required Skills* (one per line)",
                placeholder="Python\nAWS\nDocker\nKubernetes",
                height=150
            )
            
            required_experience_years = st.number_input(
                "Required Years of Experience",
                min_value=0,
                max_value=30,
                value=5
            )
        
        with col2:
            preferred_skills_text = st.text_area(
                "Preferred Skills (one per line)",
                placeholder="React\nTypeScript\nCI/CD",
                height=150
            )
            
            required_education = st.text_input(
                "Required Education",
                placeholder="Bachelor's degree in Computer Science or related field"
            )
        
        # Company Culture
        st.markdown("### 🏢 Company Culture")
        
        col1, col2 = st.columns(2)
        
        with col1:
            values_text = st.text_area(
                "Company Values (one per line)",
                placeholder="Innovation\nCollaboration\nIntegrity\nExcellence",
                height=100
            )
            
            work_style = st.text_input(
                "Work Style",
                placeholder="e.g., Fast-paced, collaborative"
            )
            
            pace = st.selectbox(
                "Work Pace",
                ["Fast-paced", "Moderate", "Methodical"]
            )
        
        with col2:
            innovation_focus = st.checkbox("Innovation Focused", value=True)
            
            collaboration_level = st.select_slider(
                "Collaboration Level",
                options=["Low", "Medium", "High"],
                value="High"
            )
            
            hierarchy = st.selectbox(
                "Organizational Structure",
                ["Flat", "Moderate", "Hierarchical"]
            )
            
            mission_driven = st.checkbox("Mission Driven", value=True)
        
        # Compensation
        st.markdown("### 💰 Compensation")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            salary_min = st.number_input(
                "Minimum Salary ($)",
                min_value=0,
                value=100000,
                step=5000
            )
        
        with col2:
            salary_max = st.number_input(
                "Maximum Salary ($)",
                min_value=0,
                value=150000,
                step=5000
            )
        
        with col3:
            salary_currency = st.text_input("Currency", value="USD")
        
        # Submit Button
        submitted = st.form_submit_button("💾 Save Job Description", use_container_width=True)
        
        if submitted:
            # Validate required fields
            if not job_id or not title or not location or not description:
                st.error("Please fill in all required fields marked with *")
            elif not required_skills_text.strip():
                st.error("Please add at least one required skill")
            else:
                # Parse lists
                responsibilities = [r.strip() for r in responsibilities_text.split('\n') if r.strip()]
                required_skills = [s.strip() for s in required_skills_text.split('\n') if s.strip()]
                preferred_skills = [s.strip() for s in preferred_skills_text.split('\n') if s.strip()]
                values = [v.strip() for v in values_text.split('\n') if v.strip()]
                
                # Create job description object
                job_data = {
                    "id": job_id,
                    "title": title,
                    "department": department,
                    "location": location,
                    "work_location_type": work_location_type.lower().replace("-", "_"),
                    "experience_level": experience_level.lower(),
                    "description": description,
                    "responsibilities": responsibilities,
                    "requirements": {
                        "required_skills": required_skills,
                        "preferred_skills": preferred_skills,
                        "required_experience_years": required_experience_years,
                        "required_education": required_education
                    },
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "salary_currency": salary_currency,
                    "compensation_range": f"${salary_min:,}-${salary_max:,}",
                    "company_culture": {
                        "values": values,
                        "work_style": work_style,
                        "pace": pace,
                        "innovation_focus": innovation_focus,
                        "collaboration_level": collaboration_level.lower(),
                        "hierarchy": hierarchy.lower(),
                        "mission_driven": mission_driven
                    },
                    "status": "active",
                    "created_at": datetime.now().isoformat()
                }
                
                # Save to file
                save_job_description(job_data)
                
                st.success(f"✅ Job Description '{title}' created successfully!")
                st.balloons()
                
                # Show preview
                with st.expander("📄 View Created Job Description"):
                    st.json(job_data)


def save_job_description(job_data):
    """Save job description to file"""
    # Create directory if it doesn't exist
    jobs_dir = Path("data/jobs")
    jobs_dir.mkdir(parents=True, exist_ok=True)
    
    # Save individual job
    job_file = jobs_dir / f"{job_data['id']}.json"
    with open(job_file, 'w') as f:
        json.dump(job_data, f, indent=2)
    
    # Update jobs list
    jobs_list_file = jobs_dir / "jobs_list.json"
    
    if jobs_list_file.exists():
        with open(jobs_list_file, 'r') as f:
            jobs_list = json.load(f)
    else:
        jobs_list = []
    
    # Update or add job
    job_exists = False
    for i, job in enumerate(jobs_list):
        if job['id'] == job_data['id']:
            jobs_list[i] = job_data
            job_exists = True
            break
    
    if not job_exists:
        jobs_list.append(job_data)
    
    with open(jobs_list_file, 'w') as f:
        json.dump(jobs_list, f, indent=2)


def render_active_jobs():
    """Display list of active jobs"""
    
    st.subheader("Active Job Descriptions")
    
    jobs_list_file = Path("data/jobs/jobs_list.json")
    
    if not jobs_list_file.exists():
        st.info("No job descriptions created yet. Create one in the 'Create New Job' tab!")
        return
    
    with open(jobs_list_file, 'r') as f:
        jobs = json.load(f)
    
    if not jobs:
        st.info("No job descriptions found.")
        return
    
    # Display jobs in cards
    for job in jobs:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"### {job['title']}")
                st.caption(f"📍 {job['location']} • {job.get('work_location_type', 'N/A').title()}")
            
            with col2:
                st.metric("Required Skills", len(job['requirements']['required_skills']))
                st.caption(f"Experience: {job['requirements'].get('required_experience_years', 'N/A')} years")
            
            with col3:
                st.markdown(f"**ID:** `{job['id']}`")
                if st.button("View", key=f"view_{job['id']}"):
                    st.session_state['selected_job'] = job['id']
            
            st.divider()


def render_job_details():
    """Display detailed job information"""
    
    st.subheader("Job Description Details")
    
    jobs_list_file = Path("data/jobs/jobs_list.json")
    
    if not jobs_list_file.exists():
        st.info("No job descriptions available.")
        return
    
    with open(jobs_list_file, 'r') as f:
        jobs = json.load(f)
    
    if not jobs:
        st.info("No jobs found.")
        return
    
    # Job selector
    job_titles = {job['id']: job['title'] for job in jobs}
    selected_job_id = st.selectbox(
        "Select Job",
        options=list(job_titles.keys()),
        format_func=lambda x: job_titles[x]
    )
    
    # Find selected job
    selected_job = next((job for job in jobs if job['id'] == selected_job_id), None)
    
    if selected_job:
        # Display job details
        st.markdown(f"## {selected_job['title']}")
        st.markdown(f"**Location:** {selected_job['location']}")
        st.markdown(f"**Department:** {selected_job.get('department', 'N/A')}")
        
        st.markdown("### Description")
        st.write(selected_job['description'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Required Skills")
            for skill in selected_job['requirements']['required_skills']:
                st.markdown(f"- ✅ {skill}")
            
            st.markdown("### Responsibilities")
            for resp in selected_job['responsibilities']:
                st.markdown(f"- {resp}")
        
        with col2:
            st.markdown("### Preferred Skills")
            for skill in selected_job['requirements'].get('preferred_skills', []):
                st.markdown(f"- ⭐ {skill}")
            
            st.markdown("### Company Culture")
            culture = selected_job.get('company_culture', {})
            st.write(f"**Pace:** {culture.get('pace', 'N/A')}")
            st.write(f"**Collaboration:** {culture.get('collaboration_level', 'N/A').title()}")
            st.write(f"**Innovation Focus:** {'Yes' if culture.get('innovation_focus') else 'No'}")
        
        # Download as JSON
        if st.button("📥 Download Job Description"):
            st.download_button(
                label="Download JSON",
                data=json.dumps(selected_job, indent=2),
                file_name=f"{selected_job['id']}.json",
                mime="application/json"
            )