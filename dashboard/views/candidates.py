
import streamlit as st

def render_candidates_page():
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

    st.title("👥 Candidates")

    tab1, tab2 = st.tabs(["📋 All Candidates", "📤 Upload Resumes"])

    # =========================
    # TAB 1: SHOW CANDIDATES
    # =========================
    with tab1:
        st.subheader("Candidate Rankings")

        all_candidates = st.session_state.get("candidates", [])

        if not all_candidates:
            st.info("No candidates yet. Upload resumes to see results.")
        else:
            # 🔥 FILTER BY JOB
            job_ids = list(set(c.get("job_id", "Unknown") for c in all_candidates))

            selected_job_filter = st.selectbox(
                "Filter by Job",
                options=["All"] + job_ids
            )

            if selected_job_filter == "All":
                candidates = all_candidates
            else:
                candidates = [
                    c for c in all_candidates
                    if c.get("job_id") == selected_job_filter
                ]

            # sort by score
            candidates = sorted(
                candidates,
                key=lambda x: x.get("overall_score", 0),
                reverse=True
            )

            if candidates:
                top = candidates[0]
                st.success(f"🏆 Top Candidate: {top.get('name', 'Unknown')}")

            for c in candidates:
                st.markdown("---")

                name = c.get("name") or \
                       c.get("candidate_data", {}).get("personal_info", {}).get("name", "Unknown")

                email = c.get("email", "N/A")
                score = c.get("overall_score", 0)
                job_id = c.get("job_id", "N/A")

                st.subheader(name)
                st.write(f"📧 {email}")
                st.write(f"💼 Job ID: {job_id}")
                st.write(f"⭐ Score: {score}%")

                st.progress(score / 100)

    # =========================
    # TAB 2: UPLOAD RESUMES
    # =========================
    with tab2:
        st.subheader("Upload Resumes")

        # 🔥 LOAD JOBS FROM DATABASE
        from storage.jobs_db import get_jobs

        jobs = get_jobs()

        if not jobs:
            st.warning("⚠️ No jobs found. Please create a job first.")
            return

        job_map = {job["id"]: job for job in jobs}

        selected_job_id = st.selectbox(
            "Select Job",
            options=list(job_map.keys()),
            format_func=lambda x: job_map[x]["title"]
        )

        selected_job = job_map[selected_job_id]

        uploaded_files = st.file_uploader(
            "Upload resumes",
            type=["pdf", "docx"],
            accept_multiple_files=True
        )

        if uploaded_files:
            st.success(f"{len(uploaded_files)} file(s) selected")

            if st.button("🚀 Process Resumes"):
                st.info("Processing...")

                from tools.pdf_parser import extract_text_from_pdf
                from tools.docx_parser import extract_text_from_docx
                from agents.orchestrator_agent import OrchestratorAgent
                import asyncio

                resumes = []

                for file in uploaded_files:
                    with open(file.name, "wb") as f:
                        f.write(file.getbuffer())

                    if file.name.endswith(".pdf"):
                        text = extract_text_from_pdf(file.name)
                    else:
                        text = extract_text_from_docx(file.name)

                    resumes.append({
                        "filename": file.name,
                        "resume_content": text
                    })

                # 🔥 USE REAL JOB DATA
                job_description = {
                    "title": selected_job["title"],
                    "required_skills": selected_job["requirements"]["required_skills"]
                }

                orchestrator = OrchestratorAgent()

                async def run():
                    return await orchestrator.process({
                        "resumes": resumes,
                        "job_description": job_description
                    })

                result = asyncio.run(run())

                st.write("DEBUG RESULT:", result)

                if result.get("ranked_candidates"):
                    # 🔥 ADD JOB ID TO EACH CANDIDATE
                    for c in result["ranked_candidates"]:
                        c["job_id"] = selected_job_id

                    # 🔥 STORE IN SESSION
                    existing = st.session_state.get("candidates", [])
                    st.session_state["candidates"] = existing + result["ranked_candidates"]

                    st.success("✅ Candidates stored successfully")
                    st.rerun()
                else:
                    st.error("❌ No candidates returned")