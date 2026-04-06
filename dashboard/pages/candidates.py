import streamlit as st


def render_candidates_page():
    st.title("👥 Candidates")

    tab1, tab2 = st.tabs(["📋 All Candidates", "📤 Upload Resumes"])

    with tab1:
        render_candidates_list()

    with tab2:
        render_upload_interface()


# =========================
# ✅ FIXED LIST VIEW
# =========================
def render_candidates_list():
    st.markdown("### Candidate Rankings")

    # 🔥 NO DATABASE (fix blank screen)
    candidates = st.session_state.get("candidates", [])

    if not candidates:
        st.info("No candidates yet. Upload resumes to see results.")
        return

    for c in candidates:
        st.markdown(f"### {c['name']}")
        st.write(f"Score: {c['overall_score']}%")
        st.write(f"Skills: {c['skills_match_score']}%")
        st.write(f"Cultural Fit: {c['cultural_fit_score']}%")
        st.write("---")


# =========================
# ✅ UPLOAD UI
# =========================
def render_upload_interface():
    st.markdown("### Upload Candidate Resumes")

    from pathlib import Path
    import json

    jobs_file = Path("data/jobs/jobs_list.json")

    if not jobs_file.exists():
        st.warning("Create a job first in Jobs page")
        return

    with open(jobs_file) as f:
        jobs = json.load(f)

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

        for f in uploaded_files:
            st.write(f"📄 {f.name}")

        if st.button("🚀 Process Resumes"):

            st.success("Processing started... please wait ⏳")

            progress = st.progress(0)
            status = st.empty()

            try:
                status.text("Saving files...")
                progress.progress(30)

                results = process_uploaded_resumes(uploaded_files, job_id)

                progress.progress(100)
                status.text("✅ Done!")

                # 🔥 Store in session (fix blank page)
                st.session_state["candidates"] = results

                st.success("Candidates processed successfully!")

            except Exception as e:
                st.error(str(e))


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
    with open(jobs_file) as f:
        jobs = json.load(f)

    job_data = next((j for j in jobs if j["id"] == job_id), None)

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

    if result["status"] == "success":
        st.success("✅ Processing complete!")

        return result["ranked_candidates"]

    else:
        st.error("Processing failed")
        return []