

"""
Jobs page for managing job descriptions (SQLite version)
"""

import streamlit as st
from datetime import datetime

# ✅ DATABASE IMPORTS
from storage.jobs_db import init_db, save_job, get_jobs, delete_job

# 🔥 Initialize DB once
init_db()


# =========================
# MAIN PAGE
# =========================
def render_jobs_page():
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.button("🏠 Home"):
            st.session_state["page"] = "Home"
        st.rerun()

    col1, col2 = st.columns([8, 1])
    with col2:
        if st.button("🏠 Home"):
            st.session_state["page"] = "Home"
            st.rerun()

    st.title("📋 Job Descriptions")

    tab1, tab2 = st.tabs(["Active Jobs", "Create / Edit Job"])

    with tab1:
        render_active_jobs()

    with tab2:
        render_create_job()


# =========================
# CREATE / EDIT JOB FORM
# =========================
def render_create_job():
    st.subheader("Create / Edit Job")

    editing_job = st.session_state.get("edit_job", None)

    with st.form("job_form"):
        col1, col2 = st.columns(2)

        with col1:
            job_id = st.text_input(
                "Job ID",
                value=editing_job.get("id") if editing_job else ""
            )
            title = st.text_input(
                "Title",
                value=editing_job.get("title") if editing_job else ""
            )

        with col2:
            location = st.text_input(
                "Location",
                value=editing_job.get("location") if editing_job else ""
            )

            experience_levels = ["Entry", "Junior", "Mid", "Senior"]

            selected_exp = editing_job.get("experience_level", "Entry") if editing_job else "Entry"

            experience = st.selectbox(
                "Experience Level",
                experience_levels,
                index=experience_levels.index(selected_exp)
            )

        description = st.text_area(
            "Description",
            value=editing_job.get("description") if editing_job else ""
        )

        skills_text = st.text_area(
            "Required Skills (comma separated)",
            value=", ".join(
                editing_job.get("requirements", {}).get("required_skills", [])
            ) if editing_job else ""
        )

        submit = st.form_submit_button("💾 Save Job")

        if submit:
            if not job_id or not title:
                st.error("Job ID and Title are required")
                return

            job_data = {
                "id": job_id,
                "title": title,
                "location": location,
                "experience_level": experience,
                "description": description,
                "requirements": {
                    "required_skills": [
                        s.strip() for s in skills_text.split(",") if s.strip()
                    ]
                },
                "created_at": datetime.now().isoformat()
            }

            # ✅ SAVE TO DATABASE (NOT JSON)
            save_job(job_data)

            # clear edit state
            if "edit_job" in st.session_state:
                del st.session_state["edit_job"]

            st.success("✅ Job saved successfully!")
            st.rerun()


# =========================
# ACTIVE JOBS (DB VERSION)
# =========================
def render_active_jobs():
    st.subheader("Active Jobs")

    # ✅ LOAD FROM DATABASE
    jobs = get_jobs()

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
                # ✏️ EDIT
                if st.button("✏️ Edit", key=f"edit_{job['id']}_{i}"):
                    st.session_state["edit_job"] = job
                    st.rerun()

            with col4:
                # ❌ DELETE (DB)
                if st.button("❌ Delete", key=f"delete_{job['id']}_{i}"):
                    delete_job(job["id"])
                    st.success(f"🗑️ Deleted {job['title']}")
                    st.rerun()

            st.divider()