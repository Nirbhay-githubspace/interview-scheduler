import streamlit as st

def render_candidates_page():
    st.title("👥 Candidates")

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
            # sort by score
            candidates = sorted(
                candidates,
                key=lambda x: x.get("overall_score", 0),
                reverse=True
            )

            # 🏆 top candidate
            top = candidates[0]
            st.success(f"🏆 Top Candidate: {top.get('name', 'Unknown')}")

            for c in candidates:
                st.markdown("---")

                # ✅ FIX: correct name extraction
                name = c.get("name") or \
                       c.get("candidate_data", {}).get("personal_info", {}).get("name", "Unknown")

                email = c.get("email", "N/A")
                score = c.get("overall_score", 0)

                st.subheader(name)
                st.write(f"📧 {email}")
                st.write(f"⭐ Score: {score}%")

                st.progress(score / 100)

    # =========================
    # TAB 2: UPLOAD (KEEP YOUR EXISTING CODE)
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

                orchestrator = OrchestratorAgent()

                async def run():
                    return await orchestrator.process({
                        "resumes": resumes,
                        "job_description": {
                            "required_skills": ["Python", "AWS", "Docker"]
                        }
                    })

                result = asyncio.run(run())

                st.write("DEBUG RESULT:", result)

                if result.get("ranked_candidates"):
                    st.session_state["candidates"] = result["ranked_candidates"]

                    st.success("✅ Candidates stored successfully")
                    st.rerun()
                else:
                    st.error("❌ No candidates returned")