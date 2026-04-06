import streamlit as st

def render_candidates_page():
    st.title("👥 Candidates")

    # 🔥 FORCE EXECUTION CONFIRMATION
    st.write("✅ Candidates page loaded successfully")

    tab1, tab2 = st.tabs(["📋 All Candidates", "📤 Upload Resumes"])

    # =========================
    # TAB 1
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

            st.success(f"🏆 Top Candidate: {candidates[0]['name']}")

            for c in candidates:
                st.markdown(f"### {c.get('name')}")
                st.write(f"Score: {c.get('overall_score')}%")
                st.progress(c.get("overall_score", 0) / 100)
                st.divider()

    # =========================
    # TAB 2
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

            if st.button("Process"):
                st.info("Processing...")

                # FAKE DATA (TEMP TEST)
                st.session_state["candidates"] = [
                    {
                        "name": "Test Candidate",
                        "overall_score": 85
                    }
                ]

                st.rerun()