import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Results Dashboard",
    page_icon="📊",
    layout="wide"
)

def create_skill_donut_chart(matching_skills, missing_skills):
    """Creates a donut chart visualizing the skill match."""
    labels = ['Matching Skills', 'Missing Skills']
    values = [len(matching_skills), len(missing_skills)]
    
    if sum(values) == 0: # Handle case with no skills in JD
        return None
        
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5,
                                marker_colors=['#4CAF50', '#F44336'])])
    fig.update_layout(
        title_text='Skill Match Breakdown',
        showlegend=True,
        height=300,
        margin=dict(t=50, b=0, l=0, r=0)
    )
    return fig

def display_skills(skill_list, color):
    """Displays a list of skills as colored buttons."""
    # The CSS is injected to style the buttons to look like tags
    st.markdown(f"""
        <style>
            .skill-tag {{
                display: inline-block;
                padding: 0.3em 0.6em;
                font-size: 0.85em;
                font-weight: 500;
                line-height: 1;
                color: #fff;
                text-align: center;
                white-space: nowrap;
                vertical-align: baseline;
                border-radius: 0.25rem;
                background-color: {color};
                margin: 0.1rem;
            }}
        </style>
    """, unsafe_allow_html=True)
    
    html_skills = "".join([f'<span class="skill-tag">{skill}</span>' for skill in skill_list])
    st.markdown(html_skills, unsafe_allow_html=True)


# --- Main Dashboard Logic ---
st.title("📊 Results Dashboard")

# Check if analysis has been run
if not st.session_state.get('analysis_done', False):
    st.warning("Please upload resumes and a job description on the main page first.")
    st.stop()

# Get the results DataFrame from session state
results_df = st.session_state.results_df

# Sort candidates by match score
results_df_sorted = results_df.sort_values(by="Match Score", ascending=False).reset_index(drop=True)

# --- Top Metrics Section ---
st.header("Top Insights")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Applicants", f"{len(results_df_sorted)}")
with col2:
    top_candidate_name = results_df_sorted.iloc[0]['Name'] if not results_df_sorted.empty else "N/A"
    st.metric("Top Candidate", top_candidate_name)
with col3:
    avg_score = results_df_sorted['Match Score'].mean() if not results_df_sorted.empty else 0
    st.metric("Average Match Score", f"{avg_score:.2f}%")

st.divider()

# --- Candidate Details Section ---
st.header("Candidate Breakdown")

# Initialize session state for shortlisting
if 'shortlisted_candidates' not in st.session_state:
    st.session_state.shortlisted_candidates = []

# Create tabs for All Candidates and Shortlisted Candidates
tab1, tab2 = st.tabs(["All Candidates", f"Shortlisted ({len(st.session_state.shortlisted_candidates)})"])

with tab1:
    if results_df_sorted.empty:
        st.info("No candidates to display.")
    else:
        for index, row in results_df_sorted.iterrows():
            with st.expander(f"**{row.get('Name', 'N/A')}** - {row['Match Score']}% Match"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.subheader("Contact Info")
                    st.text(f"Email: {row.get('Email', 'Not Found')}")
                    st.text(f"Phone: {row.get('Phone', 'Not Found')}")

                    st.subheader("Match Score")
                    st.progress(int(row['Match Score']))
                    
                    # Shortlist button
                    if row['Filename'] not in st.session_state.shortlisted_candidates:
                        if st.button("Add to Shortlist ⭐", key=f"shortlist_{index}"):
                            st.session_state.shortlisted_candidates.append(row['Filename'])
                            st.rerun() # Rerun to update the shortlisted count
                    else:
                        st.success("Shortlisted ✅")

                with col2:
                    st.subheader("Skill Analysis")
                    chart = create_skill_donut_chart(row['Matching Skills'], row['Missing Skills'])
                    if chart:
                        st.plotly_chart(chart, use_container_width=True)
                    
                    st.write("**✅ Matching Skills:**")
                    display_skills(row['Matching Skills'], '#4CAF50') # Green
                    
                    st.write("**❌ Missing Skills:**")
                    display_skills(row['Missing Skills'], '#F44336') # Red
                    
with tab2:
    st.header("Shortlisted Candidates")
    shortlisted_df = results_df_sorted[results_df_sorted['Filename'].isin(st.session_state.shortlisted_candidates)]
    
    if shortlisted_df.empty:
        st.info("No candidates have been shortlisted yet. Add candidates from the 'All Candidates' tab.")
    else:
        for index, row in shortlisted_df.iterrows():
            st.subheader(f"**{row.get('Name', 'N/A')}** - {row['Match Score']}%")
            st.text(f"Email: {row.get('Email', 'Not Found')} | Phone: {row.get('Phone', 'Not Found')}")
            
            # Button to remove from shortlist
            if st.button("Remove from Shortlist 🗑️", key=f"remove_{index}"):
                st.session_state.shortlisted_candidates.remove(row['Filename'])
                st.rerun() # Rerun to update the list
            st.divider()
