import streamlit as st
from pathlib import Path
import json

JOBS_FILE = Path("data/jobs/jobs_list.json")

def render_jobs_page():
    st.title("📋 Jobs")

    tab1, tab2 = st.tabs(["➕ Create Job", "📄 View Jobs"])

    # =========================
    # CREATE JOB
    # =========================
    with tab1:
        st.subheader("Create New Job")

        job_id = st.text_input("Job ID")
        title = st.text_input("Job Title")
        required_skills = st.text_input("Required Skills (comma separated)")
        description = st.text_area("Job Description")

        if st.button("Create Job"):
            job = {
                "id": job_id,
                "title": title,
                "requirements": {
                    "required_skills": [s.strip() for s in required_skills.split(",")]
                },
                "description": description
            }

            jobs = []

            if JOBS_FILE.exists():
                with open(JOBS_FILE, "r") as f:
                    jobs = json.load(f)

            jobs.append(job)

            JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)

            with open(JOBS_FILE, "w") as f:
                json.dump(jobs, f, indent=2)

            st.success("✅ Job created successfully!")

    # =========================
    # VIEW + DELETE JOBS
    # =========================
    with tab2:
        st.subheader("All Jobs")

        if not JOBS_FILE.exists():
            st.info("No jobs available.")
            return

        with open(JOBS_FILE, "r") as f:
            jobs = json.load(f)

        if not jobs:
            st.info("No jobs found.")
            return

        for i, job in enumerate(jobs):
            with st.container():
                st.markdown("---")

                st.markdown(f"### {job['title']}")
                st.write(f"🆔 ID: {job['id']}")

                skills = job.get("requirements", {}).get("required_skills", [])
                st.write(f"🧠 Skills: {', '.join(skills)}")

                st.write(f"📄 {job.get('description', '')}")

                col1, col2 = st.columns([4, 1])

                with col2:
                    # 🔥 DELETE BUTTON
                    if st.button("❌ Delete", key=f"delete_{job['id']}"):
                        jobs.pop(i)

                        with open(JOBS_FILE, "w") as f:
                            json.dump(jobs, f, indent=2)

                        st.success("🗑️ Job deleted!")
                        st.rerun()