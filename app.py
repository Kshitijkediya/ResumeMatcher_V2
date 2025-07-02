import streamlit as st
import pandas as pd
from modules.extractor import extract_text_from_file, extract_contact_info, extract_skills
from modules.utils import calculate_similarity

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Resume Matcher",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- Session State Initialization ---
# Initialize session state variables to ensure they persist across pages
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'results_df' not in st.session_state:
    st.session_state.results_df = None
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

# --- UI Components ---
st.title("🤖 AI-Powered Resume Matcher")
st.markdown("""
Welcome to the future of recruitment! This application leverages AI to intelligently analyze, rank, and match candidate resumes against your job descriptions.

**How to get started:**
1.  Paste the job description in the text area below.
2.  Upload one or more candidate resumes (PDF or DOCX).
3.  Click the 'Analyze Resumes' button to process the files.
4.  Navigate to the 'Dashboard' page from the sidebar to view the detailed results.
""")
st.divider()

# Input fields for job description and resume uploads
job_description_input = st.text_area("Enter the Job Description Here:", height=250, key="jd_input")
uploaded_files = st.file_uploader(
    "Upload Candidate Resumes (PDF or DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

# --- Processing Logic ---
if st.button("Analyze Resumes", type="primary", use_container_width=True):
    if not job_description_input:
        st.warning("Please paste a job description.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        with st.spinner("Analyzing... Please wait."):
            # Store job description in session state
            st.session_state.job_description = job_description_input
            
            # Process each uploaded file
            results = []
            for file in uploaded_files:
                # Extract text from resume
                resume_text = extract_text_from_file(file)
                
                # Extract skills from job description and resume
                jd_skills = extract_skills(st.session_state.job_description)
                resume_skills = extract_skills(resume_text)
                
                # Find matching and missing skills
                matching_skills = list(set(jd_skills) & set(resume_skills))
                missing_skills = list(set(jd_skills) - set(resume_skills))
                
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
                    "Resume Text": resume_text, # Store for detailed view
                })
            
            # Create DataFrame and store in session state
            st.session_state.results_df = pd.DataFrame(results)
            st.session_state.analysis_done = True
            
        st.success("Analysis Complete! ✅")
        st.info("Navigate to the 'Dashboard' page from the sidebar to see the results.")