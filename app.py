import streamlit as st
import pandas as pd
from modules.extractor import extract_text_from_file, extract_contact_info, extract_skills
from modules.utils import calculate_similarity

st.set_page_config(
    page_title="AI Resume Matcher",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto"
)

if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'job_skills' not in st.session_state:
    st.session_state.job_skills = []
if 'results_df' not in st.session_state:
    st.session_state.results_df = None
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

# --- UI Components ---
st.title("🤖 AI-Powered Intelligent Resume Matcher")
st.markdown("""
This tool intelligently analyzes, ranks, and matches resumes against your job descriptions.
The analysis is now **dynamic**: it will identify required skills directly from the job description you provide.
""")
st.divider()

# Input fields for job description and resume uploads
job_description_input = st.text_area("Enter the Job Description Here:", height=250, key="jd_input")
additional_skills_input = st.text_input("Enter Additional Skills (comma-separated)", placeholder="e.g., SwiftUI, Kotlin, Jetpack Compose")

uploaded_files = st.file_uploader(
    "Upload Candidate Resumes (PDF or DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

if st.button("Analyze Resumes", type="primary", use_container_width=True):
    if not job_description_input:
        st.warning("Please paste a job description.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        with st.spinner("Analyzing... This may take a moment."):
            st.session_state.job_description = job_description_input
            
            # --- DYNAMIC SKILL LOGIC ---
            # 1. Extract skills from the job description text
            jd_skills = set(extract_skills(st.session_state.job_description))
            
            # 2. Add skills from the manual input box
            if additional_skills_input:
                manual_skills = {skill.strip().lower() for skill in additional_skills_input.split(',')}
                jd_skills.update(manual_skills)
            
            st.session_state.job_skills = sorted(list(jd_skills)) # Store the final list of skills to check
            
            if not st.session_state.job_skills:
                st.warning("Could not identify any skills in the job description. Please add some in the 'Additional Skills' box.")
                st.stop()

            # Process each uploaded file against the dynamic skill list
            results = []
            for file in uploaded_files:
                resume_text = extract_text_from_file(file)
                
                # Extract skills found in the resume
                resume_skills = extract_skills(resume_text)
                
                # Compare against the dynamically generated list of job skills
                matching_skills = list(st.session_state.job_skills & set(resume_skills))
                missing_skills = list(set(st.session_state.job_skills) - set(resume_skills))
                
                # Calculate match score
                match_score = calculate_similarity(resume_text, st.session_state.job_description)
                
                # Extract contact information
                contact_info = extract_contact_info(resume_text)
                
                results.append({
                    "Filename": file.name,
                    "Name": contact_info.get('name'),
                    "Email": contact_info.get('email'),
                    "Phone": contact_info.get('phone'),
                    "Match Score": match_score,
                    "Matching Skills": matching_skills,
                    "Missing Skills": missing_skills,
                    "Resume Text": resume_text,
                })
            
            st.session_state.results_df = pd.DataFrame(results)
            st.session_state.analysis_done = True
            
        st.success("Analysis Complete! ✅")
        st.info(f"Analyzed against these skills: {', '.join(st.session_state.job_skills)}")
        st.info("Navigate to the 'Dashboard' page from the sidebar to see the results.")
