import streamlit as st
import os
from tools.pdf_parser import extract_text_from_pdf
from agents.orchestrator_agent import OrchestratorAgent
import asyncio
import json

st.title("AI Interview Scheduler")

# Upload PDF
uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if uploaded_file:
    st.success("File uploaded successfully!")

    # Save uploaded file temporarily
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    # Extract text
    try:
        text = extract_text_from_pdf("temp.pdf")
        st.write("Resume extracted successfully")
    except Exception as e:
        st.error(f"Error extracting PDF: {e}")
        st.stop()

    # Load job data
    with open("data/jobs/jobs_list.json") as f:
        jobs = json.load(f)

    job_data = jobs[0]

    job_description = {
        'title': job_data.get('title'),
        'required_skills': job_data.get('requirements', {}).get('required_skills', []),
        'preferred_skills': job_data.get('requirements', {}).get('preferred_skills', []),
        'experience_level': job_data.get('experience_level'),
        'description': job_data.get('description'),
        'responsibilities': job_data.get('responsibilities', [])
    }

    company_culture = job_data.get('company_culture', {})

    resumes = [{
        'filename': uploaded_file.name,
        'resume_content': text
    }]

    if st.button("Run AI Evaluation"):
        st.write("Processing... please wait ⏳")

        orchestrator = OrchestratorAgent()

        async def run():
            return await orchestrator.process({
                'resumes': resumes,
                'job_description': job_description,
                'company_culture': company_culture,
                'interviewer_email': None
            })

        result = asyncio.run(run())

        if result['status'] == 'success':
            st.success("Processing complete!")

            for candidate in result['ranked_candidates']:
                st.write("### Candidate Result")
                st.write(candidate)
        else:
            st.error(result.get("message"))