import streamlit as st

def render_candidates_page():
    st.title("👥 Candidates")

    st.write("✅ Candidates page loaded successfully")

    tab1, tab2 = st.tabs(["📋 All Candidates", "📤 Upload Resumes"])

    # =========================
    # TAB 1: SHOW CANDIDATES
    # =========================
    with tab1:
        st.subheader("Candidate Rankings")

        candidates = st.session_state.get("candidates", [])

        if not candidates:
            st.info("No candidates yet. Upload resumes to see results.")
        else:
            candidates = sorted(
                candidates,
                key=lambda x: x.get("overall_score", 0),
                reverse=True
            )

            top = candidates[0]
            st.success(f"🏆 Top Candidate: {top.get('name', 'Unknown')} ({top.get('overall_score', 0)}%)")

            for c in candidates:
                with st.container():
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.subheader(c.get("name", "Unknown"))
                        st.write(f"📧 {c.get('email', 'N/A')}")

                        skills = c.get("matched_skills", [])
                        if skills:
                            st.write("**Skills:** " + ", ".join(skills[:5]))
                        else:
                            st.write("**Skills:** None")

                    with col2:
                        st.metric("Overall", f"{c.get('overall_score', 0)}%")

                    st.progress(c.get("overall_score", 0) / 100)
                    st.divider()

    # =========================
    # TAB 2: UPLOAD + PROCESS
    # =========================
    with tab2:
        st.subheader("Upload Resumes")

        uploaded_files = st.file_uploader(
            "Upload resumes",
            type=["pdf", "docx"],
            accept_multiple_files=True
        )

        if uploaded_files:
            st.success(f"{len(uploaded_files)} file(s) selected")

            if st.button("🚀 Process Resumes"):

                st.write("🚀 Processing started...")
                progress = st.progress(0)

                try:
                    from tools.pdf_parser import extract_text_from_pdf
                    from tools.docx_parser import extract_text_from_docx
                    from agents.orchestrator_agent import OrchestratorAgent
                    import asyncio

                    resumes = []

                    # STEP 1: Extract text
                    for i, file in enumerate(uploaded_files):
                        st.write(f"📄 Processing: {file.name}")

                        path = file.name

                        with open(path, "wb") as f:
                            f.write(file.getbuffer())

                        if file.name.endswith(".pdf"):
                            text = extract_text_from_pdf(path)
                        else:
                            text = extract_text_from_docx(path)

                        resumes.append({
                            "filename": file.name,
                            "resume_content": text
                        })

                        progress.progress((i + 1) / len(uploaded_files) * 0.4)

                    st.write("✅ Resume parsing complete")

                    # STEP 2: AI Processing
                    orchestrator = OrchestratorAgent()

                    async def run():
                        return await orchestrator.process({
                            "resumes": resumes,
                            "job_description": {
                                "title": "Software Engineer",
                                "required_skills": ["Python", "Machine Learning"],
                                "preferred_skills": ["Docker"],
                                "experience_level": "mid",
                                "description": "Looking for a software engineer skilled in Python and ML",
                                "responsibilities": ["Develop models", "Write code"]
                            },
                            "company_culture": {}
                        })

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    result = loop.run_until_complete(run())

                    progress.progress(1.0)

                    # 🔥 DEBUG OUTPUT
                    st.write("DEBUG RESULT:", result)

                    # STEP 3: Handle results
                    if result.get("status") == "success":

                        candidates = result.get("ranked_candidates")

                        if not candidates:
                            st.warning("⚠️ No candidates returned from AI — using fallback")

                            candidates = [
                                {
                                    "name": "Fallback Candidate",
                                    "overall_score": 75,
                                    "email": "test@example.com",
                                    "matched_skills": ["Python"]
                                }
                            ]

                        st.session_state["candidates"] = candidates

                        st.success("✅ Processing completed! Go to 'All Candidates' tab.")

                    else:
                        st.error("❌ Processing failed")
                        st.write(result)

                except Exception as e:
                    st.error("❌ ERROR DURING PROCESSING")
                    st.write(str(e))