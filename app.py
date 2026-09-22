"""
Intelligent Resume Analyzer — Complete Streamlit Application.

Unified single-screen user journey:
1. Candidate resume ingestion and extraction (PDF)
2. Profile review (Name, Email, Phone, Skills, Education, Experience)
3. Target job description matching and multi-factor compatibility evaluation
4. In-depth analysis (Strengths, Skill Gaps, Experience & Education alignment)
5. Dual-format report export (JSON and Formatted Text)
"""

import io
import json
import logging
from datetime import datetime
from pathlib import Path
import streamlit as st

from utils.parser import parse_resume, save_parsed_resume
from utils.matcher import (
    extract_job_requirements,
    calculate_match_score,
)
from utils.reporter import (
    generate_candidate_analysis,
    generate_human_readable_report,
    save_candidate_report,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Intelligent Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Clean, professional styling using native Streamlit elements
st.markdown(
    """
    <style>
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .metric-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.15rem;
        font-weight: 600;
        color: #0F172A;
        margin-top: 4px;
        word-break: break-all;
    }
    .skill-pill {
        display: inline-block;
        background-color: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
        border-radius: 9999px;
        padding: 4px 12px;
        margin: 4px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .matched-pill {
        display: inline-block;
        background-color: #ECFDF5;
        color: #047857;
        border: 1px solid #A7F3D0;
        border-radius: 9999px;
        padding: 4px 12px;
        margin: 4px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .missing-pill {
        display: inline-block;
        background-color: #FEF2F2;
        color: #B91C1C;
        border: 1px solid #FECACA;
        border-radius: 9999px;
        padding: 4px 12px;
        margin: 4px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .strength-box {
        background-color: #F0FDF4;
        border-left: 4px solid #16A34A;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 4px;
        font-size: 0.92rem;
        color: #14532D;
    }
    .gap-box {
        background-color: #FFF7ED;
        border-left: 4px solid #EA580C;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 4px;
        font-size: 0.92rem;
        color: #7C2D12;
    }
    .score-badge-strong {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 1rem;
        display: inline-block;
    }
    .score-badge-moderate {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 1rem;
        display: inline-block;
    }
    .score-badge-low {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 1rem;
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar with UX Guidance
with st.sidebar:
    st.header("⚙️ System Overview")
    st.markdown(
        """
        **HiDevs Challenge**  
        *Intelligent Resume Analyzer*
        
        **Workflow Steps:**
        1. 📄 **Upload Resume (PDF)** $\\rightarrow$ Extract profile & skills.
        2. 📝 **Provide Job Description** $\\rightarrow$ Match qualifications.
        3. 📊 **Review Compatibility** $\\rightarrow$ Scores, strengths & gaps.
        4. 📥 **Export Reports** $\\rightarrow$ Download JSON or Text.
        """
    )
    st.divider()
    st.markdown("**Scoring Breakdown:**")
    st.markdown("- 🛠️ **Skill Match:** 70%")
    st.markdown("- 💼 **Experience Alignment:** 20%")
    st.markdown("- 🎓 **Education Qualifications:** 10%")
    st.divider()
    st.info(
        "💡 **Compatibility Note:**\n"
        "The match score is a resume-to-job compatibility score based on the configured matching criteria. "
        "It is not a hiring probability."
    )

# Application Header
st.title("Intelligent Resume Analyzer")
st.subheader("AI-assisted resume screening and job matching")
st.markdown(
    "Upload a candidate's resume and compare it against target job requirements "
    "for instant skill matching, tenure assessment, and structured reporting."
)

# State initialization
if "parsed_data" not in st.session_state:
    st.session_state.parsed_data = None
if "match_result" not in st.session_state:
    st.session_state.match_result = None
if "candidate_analysis" not in st.session_state:
    st.session_state.candidate_analysis = None
if "jd_input_text" not in st.session_state:
    st.session_state.jd_input_text = ""

# ==============================================================================
# SECTION 1: RESUME UPLOAD & PARSING
# ==============================================================================
st.markdown("---")
st.header("1. Candidate Resume Ingestion")

col_upload, col_action = st.columns([3, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "Upload PDF Resume",
        type=["pdf"],
        help="Upload a standard PDF document containing readable text.",
    )

with col_action:
    st.write("")
    st.write("")
    analyze_resume_btn = st.button("Analyze Resume", type="primary", use_container_width=True)

if analyze_resume_btn:
    if uploaded_file is None:
        st.warning("⚠️ Please select and upload a PDF resume before analyzing.")
    else:
        with st.spinner("Processing and parsing resume document..."):
            try:
                pdf_bytes = uploaded_file.read()
                if len(pdf_bytes) == 0:
                    st.error("❌ The uploaded file is empty (0 bytes). Please upload a valid PDF document.")
                else:
                    pdf_stream = io.BytesIO(pdf_bytes)
                    parsed_result = parse_resume(pdf_stream)

                    # Verify that text extraction returned meaningful content
                    has_content = any(
                        [
                            parsed_result.get("name"),
                            parsed_result.get("email"),
                            parsed_result.get("phone"),
                            parsed_result.get("skills"),
                            parsed_result.get("education"),
                            parsed_result.get("experience"),
                        ]
                    )

                    if not has_content:
                        st.warning(
                            "⚠️ No readable text could be extracted from this PDF. "
                            "It may be a scanned image or protected document without a text layer."
                        )
                    else:
                        saved_path = save_parsed_resume(parsed_result)
                        st.session_state.parsed_data = parsed_result
                        # Invalidate previous match results when a new resume is analyzed
                        st.session_state.match_result = None
                        st.session_state.candidate_analysis = None
                        st.success(f"✅ Resume successfully parsed and saved to `{saved_path.name}`!")

            except ValueError as ve:
                st.error(f"❌ Resume Parsing Error: {ve}")
                logger.error("Resume parsing ValueError: %s", ve)
            except Exception as ex:
                st.error("❌ An unexpected error occurred while reading the document. Please try again.")
                logger.exception("Unexpected error during resume parsing: %s", ex)

# Display Parsed Candidate Information
if st.session_state.parsed_data:
    data = st.session_state.parsed_data

    st.subheader("Candidate Information")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Candidate Name</div>
                <div class="metric-value">{data.get('name') or '<span style="color:#94A3B8; font-weight:normal;">Not detected</span>'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Email Address</div>
                <div class="metric-value">{data.get('email') or '<span style="color:#94A3B8; font-weight:normal;">Not detected</span>'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Phone Number</div>
                <div class="metric-value">{data.get('phone') or '<span style="color:#94A3B8; font-weight:normal;">Not detected</span>'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Technical Skills
    st.markdown(f"**Identified Technical Skills ({len(data.get('skills', []))}):**")
    skills = data.get("skills", [])
    if skills:
        pills_html = "".join([f'<span class="skill-pill">{s}</span>' for s in skills])
        st.markdown(f"<div>{pills_html}</div>", unsafe_allow_html=True)
    else:
        st.info("No matching technical skills identified from the standard dictionary.")

    st.write("")

    # Experience and Education Details
    col_exp, col_edu = st.columns(2)
    with col_exp:
        st.markdown("**Work Experience:**")
        exp_text = data.get("experience", "").strip()
        if exp_text:
            st.text_area("Experience Content", value=exp_text, height=180, label_visibility="collapsed")
        else:
            st.info("No distinct Work Experience section detected in resume.")

    with col_edu:
        st.markdown("**Education:**")
        edu_text = data.get("education", "").strip()
        if edu_text:
            st.text_area("Education Content", value=edu_text, height=180, label_visibility="collapsed")
        else:
            st.info("No distinct Education section detected in resume.")

    # ==============================================================================
    # SECTION 2: JOB DESCRIPTION MATCHING
    # ==============================================================================
    st.markdown("---")
    st.header("2. Target Job Matching")

    col_jd_label, col_jd_sample = st.columns([3, 1])
    with col_jd_label:
        st.markdown("**Enter or paste target Job Description:**")
    with col_jd_sample:
        if st.button("📝 Load Sample Job Description"):
            st.session_state.jd_input_text = (
                "Job Title: Senior Software Engineer (Python / Backend)\n\n"
                "Requirements:\n"
                "- 3+ years of professional software development experience.\n"
                "- Bachelor's degree in Computer Science, Software Engineering, or related technical field.\n"
                "- Strong hands-on proficiency in Python, FastAPI, Docker, and PostgreSQL.\n"
                "- Experience with Git, Linux, and REST APIs.\n\n"
                "Preferred Qualifications:\n"
                "- Familiarity with AWS and Kubernetes.\n"
                "- Understanding of Machine Learning or Pandas is a plus."
            )

    jd_text = st.text_area(
        "Job Description Input",
        value=st.session_state.jd_input_text,
        height=180,
        placeholder="Paste full job description requirements here...",
        label_visibility="collapsed",
    )

    analyze_match_btn = st.button("Analyze Match", type="primary", use_container_width=True)

    if analyze_match_btn:
        cleaned_jd = jd_text.strip()
        if not cleaned_jd:
            st.warning("⚠️ Please provide a Job Description before analyzing match compatibility.")
        elif len(cleaned_jd) < 30:
            st.warning("⚠️ The job description is too short to evaluate. Please provide a detailed description with required skills and criteria.")
        else:
            with st.spinner("Analyzing candidate compatibility against job criteria..."):
                try:
                    job_reqs = extract_job_requirements(cleaned_jd)
                    match_eval = calculate_match_score(data, job_reqs)
                    analysis = generate_candidate_analysis(data, job_reqs, match_eval)
                    saved_rep = save_candidate_report(analysis)

                    st.session_state.match_result = match_eval
                    st.session_state.job_reqs = job_reqs
                    st.session_state.candidate_analysis = analysis
                    st.success(f"✅ Match analysis complete! Report saved to `{saved_rep.name}`.")
                except Exception as ex:
                    st.error("❌ An error occurred while evaluating job match compatibility. Please verify your inputs.")
                    logger.exception("Error during match evaluation: %s", ex)

    # ==============================================================================
    # SECTION 3: MATCH RESULTS & SCORES
    # ==============================================================================
    if st.session_state.match_result:
        m = st.session_state.match_result
        st.markdown("---")
        st.header("3. Compatibility Assessment")

        # Top Metric Cards: Overall Score & Recommendation
        col_score_card, col_rec_card = st.columns(2)
        score_val = m["overall_score"]

        with col_score_card:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Overall Match Score</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #1E3A8A; margin-top: 4px;">
                        {score_val:.1f} <span style="font-size: 1.1rem; color: #64748B;">/ 100</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(score_val / 100.0)

        with col_rec_card:
            rec_label = m["recommendation"]
            badge_class = (
                "score-badge-strong"
                if rec_label == "Strong Match"
                else "score-badge-moderate"
                if rec_label == "Moderate Match"
                else "score-badge-low"
            )
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Recommendation</div>
                    <div style="margin-top: 10px;">
                        <span class="{badge_class}">{rec_label}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Dimension Breakdown
        st.subheader("Score Breakdown")
        b1, b2, b3 = st.columns(3)
        with b1:
            st.metric("Skill Score (70%)", f"{m['skill_score']:.1f}%")
        with b2:
            st.metric("Experience Score (20%)", f"{m['experience_score']:.1f}%")
        with b3:
            st.metric("Education Score (10%)", f"{m['education_score']:.1f}%")

        # Matched Skills & Missing Skills
        st.write("")
        col_matched, col_missing = st.columns(2)

        with col_matched:
            st.subheader(f"Matched Skills ({len(m['matched_skills'])})")
            if m["matched_skills"]:
                matched_html = "".join([f'<span class="matched-pill">✓ {s}</span>' for s in m["matched_skills"]])
                st.markdown(f"<div>{matched_html}</div>", unsafe_allow_html=True)
            else:
                st.info("No matching required skills identified.")

        with col_missing:
            st.subheader(f"Missing Skills ({len(m['missing_skills'])})")
            if m["missing_skills"]:
                missing_html = "".join([f'<span class="missing-pill">✗ {s}</span>' for s in m["missing_skills"]])
                st.markdown(f"<div>{missing_html}</div>", unsafe_allow_html=True)
            else:
                st.success("Candidate matches all primary required skills!")

    # ==============================================================================
    # SECTION 4: CANDIDATE ANALYSIS & STRENGTHS/GAPS
    # ==============================================================================
    if st.session_state.candidate_analysis:
        an = st.session_state.candidate_analysis

        # Strengths & Skill Gaps
        st.write("")
        col_str, col_gap = st.columns(2)

        with col_str:
            st.subheader(f"Strengths ({len(an.get('strengths', []))})")
            strengths = an.get("strengths", [])
            if strengths:
                for item in strengths:
                    st.markdown(f'<div class="strength-box">✓ {item}</div>', unsafe_allow_html=True)
            else:
                st.info("No specific candidate strengths documented.")

        with col_gap:
            st.subheader(f"Skill Gaps ({len(an.get('skill_gaps', []))})")
            gaps = an.get("skill_gaps", [])
            if gaps:
                for item in gaps:
                    st.markdown(f'<div class="gap-box">⚠️ {item}</div>', unsafe_allow_html=True)
            else:
                st.success("No skill gaps identified.")

        # Candidate Analysis
        st.subheader("Candidate Analysis")
        st.info(an.get("candidate_summary", "N/A"))

        # In-Depth Experience & Education Alignment
        col_an_exp, col_an_edu = st.columns(2)
        with col_an_exp:
            st.markdown("**Experience Alignment:**")
            st.write(an.get("experience_analysis", "N/A"))

        with col_an_edu:
            st.markdown("**Education Alignment:**")
            st.write(an.get("education_analysis", "N/A"))

        # Recommendation Card
        st.subheader("Recommendation")
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Assessment Conclusion</div>
                <div class="metric-value">{an.get('recommendation', 'N/A')}</div>
                <div style="font-size: 0.85rem; color: #64748B; margin-top: 8px;">
                    <em>The match score is a resume-to-job compatibility score based on the configured matching criteria. It is not a hiring probability.</em>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ==============================================================================
        # SECTION 5: REPORT DOWNLOADS
        # ==============================================================================
        st.markdown("---")
        st.subheader("Export Assessment Reports")

        human_text = generate_human_readable_report(
            an,
            candidate_info={
                "name": data.get("name"),
                "email": data.get("email"),
            },
        )
        json_report_str = json.dumps(an, indent=4, ensure_ascii=False)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        d_col1, d_col2 = st.columns(2)

        with d_col1:
            st.download_button(
                label="📥 Download JSON",
                data=json_report_str,
                file_name=f"candidate_report_{timestamp_str}.json",
                mime="application/json",
                type="primary",
                use_container_width=True,
            )

        with d_col2:
            st.download_button(
                label="📄 Download Report",
                data=human_text,
                file_name=f"candidate_report_{timestamp_str}.txt",
                mime="text/plain",
                type="secondary",
                use_container_width=True,
            )

        with st.expander("🔍 Preview Text Report"):
            st.code(human_text, language="text")
