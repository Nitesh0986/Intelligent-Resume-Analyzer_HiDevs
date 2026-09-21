"""
Streamlit Application for Intelligent Resume Analyzer.

Day 1 implementation providing:
- PDF upload interface
- Real-time text extraction and cleaning
- Named entity & section extraction (Name, Email, Phone, Skills, Education, Experience)
- Interactive candidate analysis preview
- Structured JSON export and download
"""

import io
import json
import logging
from datetime import datetime
from pathlib import Path
import streamlit as st

from utils.parser import parse_resume, save_parsed_resume

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

# Custom styling for badges and cards
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
    .section-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 18px;
        height: 100%;
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
        
        **Pipeline Flow:**
        1. 📄 **PDF Extraction** (Multi-page text extraction)
        2. 🧹 **Preprocessing** (Whitespace, bullets & ligatures)
        3. 🔍 **Information Extraction**
           - Contact Details (Email, Phone)
           - Candidate Name
           - Skills Dictionary Matching
           - Section Segmentation (Exp, Edu)
        4. 💾 **Structured JSON Export**
        """
    )
    st.divider()
    st.info("💡 **Tip:** Scanned image-only PDFs without an embedded text layer cannot be parsed without OCR.")

# Main Application Header
st.markdown('<div class="main-title">Intelligent Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">AI-assisted resume parsing and candidate analysis</div>', unsafe_allow_html=True)

# Upload Area
col_upload, col_action = st.columns([3, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "Upload Candidate Resume",
        type=["pdf"],
        help="Upload a standard PDF resume with select-able text",
    )

with col_action:
    st.write("")  # Spacing
    st.write("")
    analyze_button = st.button("🚀 Analyze Resume", type="primary", use_container_width=True)

# Persistent state management for analysis results
if "parsed_data" not in st.session_state:
    st.session_state.parsed_data = None
if "saved_file_path" not in st.session_state:
    st.session_state.saved_file_path = None

if analyze_button:
    if uploaded_file is None:
        st.warning("⚠️ Please select and upload a PDF resume before clicking Analyze.")
    else:
        with st.spinner("Processing and analyzing resume..."):
            try:
                # Read uploaded file bytes into in-memory buffer
                pdf_bytes = uploaded_file.read()
                if len(pdf_bytes) == 0:
                    st.error("❌ The uploaded file is empty (0 bytes). Please upload a valid PDF.")
                else:
                    pdf_stream = io.BytesIO(pdf_bytes)
                    parsed_result = parse_resume(pdf_stream)

                    # Check if any meaningful content was retrieved
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
                            "It may be scanned, image-only, or protected."
                        )
                    else:
                        # Save to disk
                        saved_path = save_parsed_resume(parsed_result)
                        st.session_state.parsed_data = parsed_result
                        st.session_state.saved_file_path = str(saved_path)
                        st.success(f"✅ Resume successfully parsed and saved to `{saved_path.name}`!")

            except ValueError as ve:
                st.error(f"❌ Parsing Error: {ve}")
                logger.error("ValueError during parsing: %s", ve)
            except Exception as ex:
                st.error(f"❌ An unexpected error occurred while processing the document: {ex}")
                logger.exception("Unexpected error: %s", ex)

# Display Parsed Results
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

    # Technical Skills Section
    st.markdown(f"### 🛠️ Technical Skills ({len(data.get('skills', []))})")
    skills = data.get("skills", [])
    if skills:
        pills_html = "".join([f'<span class="skill-pill">{s}</span>' for s in skills])
        st.markdown(f"<div>{pills_html}</div>", unsafe_allow_html=True)
    else:
        st.info("No matching skills detected from the predefined skills dictionary.")

    st.write("")  # Spacing

    # Sectional Breakdown (Experience & Education)
    col_exp, col_edu = st.columns(2)

    with col_exp:
        st.markdown("### 💼 Work Experience")
        exp_text = data.get("experience", "").strip()
        if exp_text:
            st.text_area("Extracted Experience", value=exp_text, height=280, label_visibility="collapsed")
        else:
            st.info("No distinct Work Experience section detected.")

    with col_edu:
        st.markdown("### 🎓 Education & Background")
        edu_text = data.get("education", "").strip()
        if edu_text:
            st.text_area("Extracted Education", value=edu_text, height=280, label_visibility="collapsed")
        else:
            st.info("No distinct Education section detected.")

    # JSON Preview and Download Actions
    st.divider()
    col_actions_left, col_actions_right = st.columns([2, 1])

    json_str = json.dumps(data, indent=4, ensure_ascii=False)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    with col_actions_left:
        with st.expander("🔍 View Structured JSON Data"):
            st.json(data)

    with col_actions_right:
        st.download_button(
            label="📥 Download Parsed JSON",
            data=json_str,
            file_name=f"parsed_resume_{timestamp_str}.json",
            mime="application/json",
            type="secondary",
            use_container_width=True,
        )
