"""
Jobs page for managing job descriptions
"""
from storage.jobs_db import init_db, save_job, get_jobs, delete_job
init_db()

import streamlit as st
import json
from pathlib import Path
from datetime import datetime


JOBS_FILE = Path("data/jobs/jobs_list.json")


# =========================
# MAIN PAGE
# =========================
def render_jobs_page():
    st.title("📋 Job Descriptions")

    tab1, tab2 = st.tabs(["Active Jobs", "Create New Job"])

    with tab1:
        render_active_jobs()

    with tab2:
        render_create_job()


# =========================
# CREATE / EDIT JOB FORM
# =========================
def render_create_job():
    st.subheader("Create / Edit Job")

    # 🔥 Check if editing
    editing_job = st.session_state.get("edit_job", None)

    with st.form("job_form"):
        col1, col2 = st.columns(2)

        with col1:
            job_id = st.text_input("Job ID", value=editing_job.get("id") if editing_job else "")
            title = st.text_input("Title", value=editing_job.get("title") if editing_job else "")

        with col2:
            location = st.text_input("Location", value=editing_job.get("location") if editing_job else "")
            experience = st.selectbox(
                "Experience Level",
                ["Entry", "Junior", "Mid", "Senior"],
                index=0 if not editing_job else ["Entry", "Junior", "Mid", "Senior"].index(editing_job.get("experience_level", "Entry"))
            )

        description = st.text_area(
            "Description",
            value=editing_job.get("description") if editing_job else ""
        )

        skills_text = st.text_area(
            "Required Skills (comma separated)",
            value=", ".join(editing_job.get("requirements", {}).get("required_skills", [])) if editing_job else ""
        )

        submit = st.form_submit_button("💾 Save Job")

        if submit:
            job_data = {
                "id": job_id,
                "title": title,
                "location": location,
                "experience_level": experience,
                "description": description,
                "requirements": {
                    "required_skills": [s.strip() for s in skills_text.split(",") if s.strip()]
                },
                "created_at": datetime.now().isoformat()
            }

            save_job(job_data)

            # 🔥 Clear edit mode
            if "edit_job" in st.session_state:
                del st.session_state["edit_job"]

            st.success("✅ Job saved successfully!")
            st.rerun()


# =========================
# SAVE JOB
# =========================
def save_job(job_data):
    JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)

    if JOBS_FILE.exists():
        with open(JOBS_FILE) as f:
            jobs = json.load(f)
    else:
        jobs = []

    # 🔥 Update if exists
    updated = False
    for i, job in enumerate(jobs):
        if job["id"] == job_data["id"]:
            jobs[i] = job_data
            updated = True
            break

    if not updated:
        jobs.append(job_data)

    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=2)


# =========================
# ACTIVE JOBS (EDIT + DELETE)
# =========================
def render_active_jobs():
    st.subheader("Active Jobs")

    if not JOBS_FILE.exists():
        st.info("No jobs yet.")
        return

    with open(JOBS_FILE) as f:
        jobs = json.load(f)

    if not jobs:
        st.info("No jobs found.")
        return

    for i, job in enumerate(jobs):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

            with col1:
                st.markdown(f"### {job['title']}")
                st.caption(f"📍 {job.get('location', 'N/A')}")

            with col2:
                st.metric("Skills", len(job["requirements"]["required_skills"]))

            with col3:
                # 🔥 EDIT BUTTON
                if st.button("✏️ Edit", key=f"edit_{job['id']}_{i}"):
                    st.session_state["edit_job"] = job
                    st.rerun()

            with col4:
                # 🔥 DELETE BUTTON
                if st.button("❌ Delete", key=f"delete_{job['id']}_{i}"):
                    jobs.pop(i)

                    with open(JOBS_FILE, "w") as f:
                        json.dump(jobs, f, indent=2)

                    st.success(f"🗑️ Deleted {job['title']}")
                    st.rerun()

            st.divider()