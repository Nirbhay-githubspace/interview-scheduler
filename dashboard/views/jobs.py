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
    
    with tabs[0]:
        render_active_jobs()
    
    with tabs[1]:
        render_create_job()
    
    with tabs[2]:
        render_job_details()


# =========================
# CREATE JOB (UNCHANGED)
# =========================
def render_create_job():
    st.subheader("Create New Job Description")
    
    with st.form("create_job_form"):
        st.markdown("### 📝 Basic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            job_id = st.text_input("Job ID*")
            title = st.text_input("Job Title*")
            department = st.text_input("Department")
        
        with col2:
            location = st.text_input("Location*")
            work_location_type = st.selectbox("Work Location Type", ["Hybrid", "Remote", "On-site"])
            experience_level = st.selectbox("Experience Level*", ["Entry", "Junior", "Mid", "Senior", "Lead", "Principal"])
        
        st.markdown("### 📄 Description")
        description = st.text_area("Job Description*", height=150)
        
        st.markdown("### 🎯 Required Skills")
        required_skills_text = st.text_area("Required Skills*", height=100)
        
        submitted = st.form_submit_button("💾 Save Job Description", use_container_width=True)
        
        if submitted:
            if not job_id or not title or not location or not description:
                st.error("Fill all required fields")
                return
            
            job_data = {
                "id": job_id,
                "title": title,
                "department": department,
                "location": location,
                "work_location_type": work_location_type,
                "experience_level": experience_level,
                "description": description,
                "requirements": {
                    "required_skills": [s.strip() for s in required_skills_text.split("\n") if s.strip()]
                },
                "created_at": datetime.now().isoformat()
            }
            
            save_job_description(job_data)
            st.success("✅ Job created!")


# =========================
# SAVE JOB
# =========================
def save_job_description(job_data):
    jobs_dir = Path("data/jobs")
    jobs_dir.mkdir(parents=True, exist_ok=True)
    
    job_file = jobs_dir / f"{job_data['id']}.json"
    with open(job_file, "w") as f:
        json.dump(job_data, f, indent=2)
    
    jobs_list_file = jobs_dir / "jobs_list.json"
    
    if jobs_list_file.exists():
        with open(jobs_list_file) as f:
            jobs = json.load(f)
    else:
        jobs = []
    
    jobs.append(job_data)
    
    with open(jobs_list_file, "w") as f:
        json.dump(jobs, f, indent=2)


# =========================
# 🔥 ACTIVE JOBS (UPDATED WITH DELETE)
# =========================
def render_active_jobs():
    
    st.subheader("Active Job Descriptions")
    
    jobs_list_file = Path("data/jobs/jobs_list.json")
    
    if not jobs_list_file.exists():
        st.info("No jobs yet")
        return
    
    with open(jobs_list_file) as f:
        jobs = json.load(f)
    
    if not jobs:
        st.info("No jobs found")
        return
    
    for i, job in enumerate(jobs):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            
            with col1:
                st.markdown(f"### {job['title']}")
                st.caption(f"📍 {job['location']}")
            
            with col2:
                st.metric("Skills", len(job["requirements"]["required_skills"]))
            
            with col3:
                if st.button("View", key=f"view_{job['id']}"):
                    st.session_state["selected_job"] = job["id"]
            
            with col4:
                # 🔥 DELETE BUTTON
                if st.button("❌ Delete", key=f"delete_{job['id']}"):
                    
                    # Remove from list
                    jobs.pop(i)
                    
                    # Save updated list
                    with open(jobs_list_file, "w") as f:
                        json.dump(jobs, f, indent=2)
                    
                    # Delete individual file
                    job_file = Path(f"data/jobs/{job['id']}.json")
                    if job_file.exists():
                        job_file.unlink()
                    
                    st.success(f"🗑️ Deleted {job['title']}")
                    st.rerun()
            
            st.divider()


# =========================
# VIEW JOB DETAILS (UNCHANGED)
# =========================
def render_job_details():
    
    st.subheader("Job Details")
    
    jobs_list_file = Path("data/jobs/jobs_list.json")
    
    if not jobs_list_file.exists():
        st.info("No jobs available")
        return
    
    with open(jobs_list_file) as f:
        jobs = json.load(f)
    
    if not jobs:
        st.info("No jobs found")
        return
    
    job_titles = {j["id"]: j["title"] for j in jobs}
    
    selected = st.selectbox(
        "Select Job",
        options=list(job_titles.keys()),
        format_func=lambda x: job_titles[x]
    )
    
    job = next(j for j in jobs if j["id"] == selected)
    
    st.markdown(f"## {job['title']}")
    st.write(job["description"])
    
    st.markdown("### Skills")
    for s in job["requirements"]["required_skills"]:
        st.write(f"- {s}")