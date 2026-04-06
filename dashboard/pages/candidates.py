import streamlit as st

st.title("👥 Candidates")

# =========================
# TABS
# =========================
tab1, tab2 = st.tabs(["📋 All Candidates", "📤 Upload Resumes"])

# =========================
# TAB 1: LIST
# =========================
with tab1:
    st.markdown("### Candidate Rankings")

    candidates = st.session_state.get("candidates", [])

    if not candidates:
        st.info("No candidates yet. Upload resumes to see results.")
    else:
        for c in candidates:
            st.markdown(f"### {c.get('name', 'Unknown')}")
            st.write(f"Score: {c.get('overall_score', 0)}%")
            st.write(f"Skills: {c.get('skills_match_score', 0)}%")
            st.write(f"Cultural Fit: {c.get('cultural_fit_score', 0)}%")
            st.write("---")

# =========================
# TAB 2: UPLOAD
# =========================
with tab2:
    st.markdown("### Upload Candidate Resumes")

    from pathlib import Path
    import json

    jobs_file = Path("data/jobs/jobs_list.json")

    if not jobs_file.exists():
        st.warning("⚠️ Create a job first in Jobs page")
    else:
        with open(jobs_file) as f:
            jobs = json.load(f)

        if not jobs:
            st.warning("⚠️ No jobs found")
        else:
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

                    from tools.pdf_parser import extract_text_from_pdf
                    from tools.docx_parser import extract_text_from_docx
                    from agents.orchestrator_agent import OrchestratorAgent
                    import asyncio

                    resumes = []

                    for file in uploaded_files:
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

                    job_data = next((j for j in jobs if j["id"] == job_id), None)

                    job_description = {
                        "title": job_data.get("title"),
                        "required_skills": job_data.get("requirements", {}).get("required_skills", []),
                        "preferred_skills": job_data.get("requirements", {}).get("preferred_skills", []),
                    }

                    company_culture = job_data.get("company_culture", {})

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

                        st.session_state["candidates"] = result.get("ranked_candidates", [])
                    else:
                        st.error("Processing failed")