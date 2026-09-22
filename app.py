"""
Streamlit Application for Intelligent Resume Analyzer.

Comprehensive Day 1, Day 2, and Day 3 implementation:
- Day 1: PDF upload, extraction, sanitization, and structured parsing
- Day 2: Job description input, requirement extraction, and compatibility matching
- Day 3: Professional candidate analysis, strengths/gaps identification, and dual-format report generation (JSON & Text)
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
    WEIGHT_SKILLS,
    WEIGHT_EXPERIENCE,
    WEIGHT_EDUCATION,
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

# Custom styling for UI elements
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .metric-label {
        font-size: 0.85rem;
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
        font-size: 0.875rem;
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
        font-size: 0.875rem;
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
        font-size: 0.875rem;
        font-weight: 600;
    }
    .strength-item {
        background-color: #F0FDF4;
        border-left: 4px solid #22C55E;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 4px;
        font-size: 0.95rem;
        color: #166534;
    }
    .gap-item {
        background-color: #FFF7ED;
        border-left: 4px solid #F97316;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 4px;
        font-size: 0.95rem;
        color: #9A3412;
    }
    .score-badge-strong {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 6px 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.05rem;
        display: inline-block;
    }
    .score-badge-moderate {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 6px 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.05rem;
        display: inline-block;
    }
    .score-badge-low {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 6px 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.05rem;
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.header("⚙️ Project Overview")
    st.markdown(
        """
        **HiDevs Challenge**  
        *Day 1: Resume Parsing Pipeline*  
        *Day 2: Job Matching Engine*  
        *Day 3: Candidate Analysis & Reports*
        
        **Matching Weights:**
        - 🛠️ **Skills Match:** 70%
        - 💼 **Experience:** 20%
        - 🎓 **Education:** 10%
        
        **Technology Stack:**
        - Pure Python 3.14
        - Streamlit Web Dashboard
        - Deterministic heuristics & regex
        - Zero external LLM APIs
        """
    )
    st.divider()
    st.info("💡 **Transparency Note:** All candidate evaluations are generated deterministically based strictly on observable resume evidence.")

# Main Application Header
st.markdown('<div class="main-title">Intelligent Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">AI-assisted resume parsing, job matching, and candidate analysis</div>', unsafe_allow_html=True)

# Session state initialization
if "parsed_data" not in st.session_state:
    st.session_state.parsed_data = None
if "saved_file_path" not in st.session_state:
    st.session_state.saved_file_path = None
if "match_result" not in st.session_state:
    st.session_state.match_result = None
if "job_reqs" not in st.session_state:
    st.session_state.job_reqs = None
if "candidate_analysis" not in st.session_state:
    st.session_state.candidate_analysis = None
if "saved_report_path" not in st.session_state:
    st.session_state.saved_report_path = None
if "jd_text_input" not in st.session_state:
    st.session_state.jd_text_input = ""

# Step 1: Upload & Parse Resume
st.markdown("## 1. Resume Ingestion")
col_upload, col_action = st.columns([3, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "Upload Candidate Resume (PDF)",
        type=["pdf"],
        help="Upload a standard PDF resume containing an embedded text layer",
    )

with col_action:
    st.write("")
    st.write("")
    analyze_button = st.button("🚀 Parse Resume", type="primary", use_container_width=True)

if analyze_button:
    if uploaded_file is None:
        st.warning("⚠️ Please select and upload a PDF resume before parsing.")
    else:
        with st.spinner("Extracting and parsing resume..."):
            try:
                pdf_bytes = uploaded_file.read()
                if len(pdf_bytes) == 0:
                    st.error("❌ The uploaded file is empty (0 bytes). Please upload a valid PDF.")
                else:
                    pdf_stream = io.BytesIO(pdf_bytes)
                    parsed_result = parse_resume(pdf_stream)

                    has_text = any(
                        [
                            parsed_result.get("name"),
                            parsed_result.get("email"),
                            parsed_result.get("phone"),
                            parsed_result.get("skills"),
                            parsed_result.get("education"),
                            parsed_result.get("experience"),
                        ]
                    )

                    if not has_text:
                        st.warning(
                            "⚠️ No readable text could be extracted from this PDF. "
                            "It may be an image-only scan or encrypted."
                        )
                    else:
                        saved_path = save_parsed_resume(parsed_result)
                        st.session_state.parsed_data = parsed_result
                        st.session_state.saved_file_path = str(saved_path)
                        # Reset downstream matching results when new resume is parsed
                        st.session_state.match_result = None
                        st.session_state.candidate_analysis = None
                        st.success(f"✅ Resume successfully parsed and saved to `{saved_path.name}`!")

            except ValueError as ve:
                st.error(f"❌ Parsing Error: {ve}")
                logger.error("ValueError during parsing: %s", ve)
            except Exception as ex:
                st.error(f"❌ Unexpected error processing document: {ex}")
                logger.exception("Unexpected error: %s", ex)

# Display Parsed Resume Data
if st.session_state.parsed_data:
    data = st.session_state.parsed_data

    st.markdown("### 📋 Candidate Profile")
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

    st.markdown(f"### 🛠️ Identified Skills ({len(data.get('skills', []))})")
    skills = data.get("skills", [])
    if skills:
        pills_html = "".join([f'<span class="skill-pill">{s}</span>' for s in skills])
        st.markdown(f"<div>{pills_html}</div>", unsafe_allow_html=True)
    else:
        st.info("No matching skills detected from the predefined skills dictionary.")

    st.write("")

    col_exp, col_edu = st.columns(2)
    with col_exp:
        st.markdown("### 💼 Work Experience")
        exp_text = data.get("experience", "").strip()
        if exp_text:
            st.text_area("Experience Section", value=exp_text, height=200, label_visibility="collapsed")
        else:
            st.info("No distinct Work Experience section detected.")

    with col_edu:
        st.markdown("### 🎓 Education & Background")
        edu_text = data.get("education", "").strip()
        if edu_text:
            st.text_area("Education Section", value=edu_text, height=200, label_visibility="collapsed")
        else:
            st.info("No distinct Education section detected.")

    # Step 2: Job Description Matching
    st.divider()
    st.markdown("## 2. Job Matching Engine")
    st.markdown("Compare the candidate's parsed qualifications against a target Job Description.")

    col_jd_head, col_sample = st.columns([3, 1])
    with col_jd_head:
        st.markdown("**Target Job Description:**")
    with col_sample:
        if st.button("📝 Load Sample Job Description"):
            st.session_state.jd_text_input = (
                "Job Title: Senior Python Engineer\n\n"
                "Requirements:\n"
                "- 3+ years of professional software engineering experience.\n"
                "- Bachelor's degree in Computer Science, Software Engineering, or related field.\n"
                "- Strong hands-on proficiency in Python, FastAPI, Docker, and PostgreSQL.\n"
                "- Experience with Git, Linux, and REST APIs.\n\n"
                "Preferred Qualifications:\n"
                "- Familiarity with AWS and Kubernetes.\n"
                "- Understanding of Machine Learning or Pandas is a plus."
            )

    jd_text = st.text_area(
        "Job Description Input",
        value=st.session_state.jd_text_input,
        height=180,
        placeholder="Paste full job description requirements here...",
        label_visibility="collapsed",
    )

    if st.button("🎯 Analyze Job Match", type="primary", use_container_width=True):
        if not jd_text.strip():
            st.warning("⚠️ Please provide a Job Description before analyzing match compatibility.")
        else:
            with st.spinner("Analyzing candidate compatibility and generating report..."):
                try:
                    job_reqs = extract_job_requirements(jd_text)
                    match_eval = calculate_match_score(data, job_reqs)
                    analysis = generate_candidate_analysis(data, job_reqs, match_eval)
                    saved_rep = save_candidate_report(analysis)

                    st.session_state.match_result = match_eval
                    st.session_state.job_reqs = job_reqs
                    st.session_state.candidate_analysis = analysis
                    st.session_state.saved_report_path = str(saved_rep)

                    st.success(f"✅ Match analysis complete! Report saved to `{saved_rep.name}`.")
                except Exception as ex:
                    st.error(f"❌ Error during match evaluation: {ex}")
                    logger.exception("Match evaluation error: %s", ex)

    # Display Matching Results
    if st.session_state.match_result:
        m = st.session_state.match_result
        st.markdown("### 📊 Compatibility Evaluation")

        score_col, rec_col = st.columns([2, 2])
        score_val = m["overall_score"]

        with score_col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Overall Compatibility Score</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #1E3A8A; margin-top: 4px;">
                        {score_val:.1f} <span style="font-size: 1.1rem; color: #64748B;">/ 100</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(score_val / 100.0)

        with rec_col:
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
                    <div class="metric-label">Evaluation Recommendation</div>
                    <div style="margin-top: 10px;">
                        <span class="{badge_class}">{rec_label}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Dimension Breakdown
        b1, b2, b3 = st.columns(3)
        with b1:
            st.metric("🛠️ Skills Match (70%)", f"{m['skill_score']:.1f}%")
        with b2:
            st.metric("💼 Experience Match (20%)", f"{m['experience_score']:.1f}%")
        with b3:
            st.metric("🎓 Education Match (10%)", f"{m['education_score']:.1f}%")

        # Matched vs Missing Skills Cards
        col_matched, col_missing = st.columns(2)

        with col_matched:
            st.markdown(f"#### ✅ Matched Skills ({len(m['matched_skills'])})")
            if m["matched_skills"]:
                matched_html = "".join([f'<span class="matched-pill">✓ {s}</span>' for s in m["matched_skills"]])
                st.markdown(f"<div>{matched_html}</div>", unsafe_allow_html=True)
            else:
                st.info("No matching required skills detected.")

        with col_missing:
            st.markdown(f"#### ⚠️ Missing Skills ({len(m['missing_skills'])})")
            if m["missing_skills"]:
                missing_html = "".join([f'<span class="missing-pill">✗ {s}</span>' for s in m["missing_skills"]])
                st.markdown(f"<div>{missing_html}</div>", unsafe_allow_html=True)
            else:
                st.success("Candidate has all primary required skills!")

    # Step 3: Professional Candidate Analysis Report
    if st.session_state.candidate_analysis:
        an = st.session_state.candidate_analysis
        st.divider()
        st.markdown("## 3. Professional Candidate Analysis & Report")

        # Executive Summary
        st.markdown("### 📌 Executive Candidate Summary")
        st.info(an.get("candidate_summary", "N/A"))

        # Strengths & Skill Gaps
        col_str, col_gap = st.columns(2)

        with col_str:
            st.markdown(f"### 🌟 Verified Strengths ({len(an.get('strengths', []))})")
            strengths = an.get("strengths", [])
            if strengths:
                for item in strengths:
                    st.markdown(f'<div class="strength-item">✓ {item}</div>', unsafe_allow_html=True)
            else:
                st.info("No specific strengths documented.")

        with col_gap:
            st.markdown(f"### 🔍 Identified Skill Gaps ({len(an.get('skill_gaps', []))})")
            gaps = an.get("skill_gaps", [])
            if gaps:
                for item in gaps:
                    st.markdown(f'<div class="gap-item">⚠️ {item}</div>', unsafe_allow_html=True)
            else:
                st.success("No skill gaps identified.")

        # Experience & Education In-Depth Alignment
        col_an_exp, col_an_edu = st.columns(2)
        with col_an_exp:
            st.markdown("### 💼 Experience Alignment")
            st.write(an.get("experience_analysis", "N/A"))

        with col_an_edu:
            st.markdown("### 🎓 Education Alignment")
            st.write(an.get("education_analysis", "N/A"))

        # Formal Recommendation
        st.markdown("### 🎯 Formal Assessment")
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">System Recommendation</div>
                <div class="metric-value">{an.get('recommendation', 'N/A')}</div>
                <div style="font-size: 0.85rem; color: #64748B; margin-top: 8px;">
                    <em>Disclaimer: This automated evaluation is an objective compatibility assessment based on observable criteria and does not constitute a final hiring decision.</em>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Report Downloads Section
        st.divider()
        st.markdown("### 📥 Export Candidate Analysis Reports")

        # Generate human-readable text report
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
                label="📥 Download JSON Report",
                data=json_report_str,
                file_name=f"candidate_report_{timestamp_str}.json",
                mime="application/json",
                type="primary",
                use_container_width=True,
            )

        with d_col2:
            st.download_button(
                label="📄 Download Text Report (.txt)",
                data=human_text,
                file_name=f"candidate_report_{timestamp_str}.txt",
                mime="text/plain",
                type="secondary",
                use_container_width=True,
            )

        with st.expander("🔍 Preview Text Report"):
            st.code(human_text, language="text")
