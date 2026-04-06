import streamlit as st

# 🔥 DEBUG LINE (keep this for now)
st.write("Candidates page loaded")


def render_candidates_page():
    st.title("👥 Candidates")

    try:
        tab1, tab2 = st.tabs(["📋 All Candidates", "📤 Upload Resumes"])

        with tab1:
            render_candidates_list()

        with tab2:
            render_upload_interface()

    except Exception as e:
        st.error("🔥 Error in Candidates Page")
        st.write(str(e))

        import traceback
        st.code(traceback.format_exc())


# =========================
# ✅ SAFE LIST VIEW
# =========================
def render_candidates_list():
    try:
        st.markdown("### Candidate Rankings")

        candidates = st.session_state.get("candidates", [])

        if not candidates:
            st.info("No candidates yet. Upload resumes to see results.")
            return

        for c in candidates:
            st.markdown(f"### {c.get('name', 'Unknown')}")
            st.write(f"Score: {c.get('overall_score', 0)}%")
            st.write(f"Skills: {c.get('skills_match_score', 0)}%")
            st.write(f"Cultural Fit: {c.get('cultural_fit_score', 0)}%")
            st.write("---")

    except Exception as e:
        st.error("🔥 Error in Candidate List")
        st.write(str(e))


# =========================
# ✅ SAFE UPLOAD UI
# =========================
def render_upload_interface():
    try:
        st.markdown("### Upload Candidate Resumes")

        from pathlib import Path
        import json

        jobs_file = Path("data/jobs/jobs_list.json")

        if not jobs_file.exists():
            st.warning("⚠️ Create a job first in Jobs page")
            return

        with open(jobs_file) as f:
            jobs = json.load(f)

        if not jobs:
            st.warning("⚠️ No jobs found")
            return

        job_options = {job["id"]: job["title"] for job in jobs}

        job_id = st.selectbox(
            "Select Job",
            options=list(job_options.keys()),
            format_func=lambda x: job_options[x],
        )

        uploaded_files = st.file_uploader(
            "Upload resumes",
            type=["pdf", "docx"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            st.success(f"{len(uploaded_files)} file(s) selected")

            if st.button("🚀 Process Resumes"):
                st.success("Processing started... ⏳")

                progress = st.progress(0)
                status = st.empty()

                try:
                    status.text("Saving files...")
                    progress.progress(30)

                    results = process_uploaded_resumes(uploaded_files, job_id)

                    progress.progress(100)
                    status.text("✅ Done!")

                    st.session_state["candidates"] = results

                    st.success("Candidates processed successfully!")

                except Exception as e:
                    st.error("🔥 Processing Error")
                    st.write(str(e))

    except Exception as e:
        st.error("🔥 Upload UI Error")
        st.write(str(e))

        import traceback
        st.code(traceback.format_exc())


# =========================
# 🔥 PROCESS FUNCTION
# =========================
def process_uploaded_resumes(files, job_id):
    import asyncio
    from pathlib import Path
    import json

    from tools.pdf_parser import extract_text_from_pdf
    from tools.docx_parser import extract_text_from_docx
    from agents.orchestrator_agent import OrchestratorAgent

    st.write("⚙️ Starting processing...")

    # Load job
    jobs_file = Path("data/jobs/jobs_list.json")

    if not jobs_file.exists():
        st.error("Job file missing")
        return []

    with open(jobs_file) as f:
        jobs = json.load(f)

    job_data = next((j for j in jobs if j["id"] == job_id), None)

    if not job_data:
        st.error("Job not found")
        return []

    job_description = {
        "title": job_data.get("title"),
        "required_skills": job_data.get("requirements", {}).get("required_skills", []),
        "preferred_skills": job_data.get("requirements", {}).get("preferred_skills", []),
    }

    company_culture = job_data.get("company_culture", {})

    resumes = []

    for file in files:
        st.write(f"Processing {file.name}")

        path = Path("temp_" + file.name)

        with open(path, "wb") as f:
            f.write(file.getbuffer())

        if file.name.endswith(".pdf"):
            text = extract_text_from_pdf(str(path))
        else:
            text = extract_text_from_docx(str(path))

        resumes.append({
            "filename": file.name,
            "resume_content": text,
        })

    orchestrator = OrchestratorAgent()

    async def run():
        return await orchestrator.process({
            "resumes": resumes,
            "job_description": job_description,
            "company_culture": company_culture,
        })

    result = asyncio.run(run())

    if result.get("status") == "success":
        st.success("✅ Processing complete!")
        return result.get("ranked_candidates", [])
    else:
        st.error("Processing failed")
        return []