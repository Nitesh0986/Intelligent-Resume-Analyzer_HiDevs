# Intelligent Resume Analyzer (HiDevs Challenge)

An AI-assisted resume parsing, job description matching, and candidate analysis engine developed in **100% Python** for the HiDevs Intelligent Resume Analyzer project.

---

## Capabilities Overview

- **Day 1: Resume Parsing Pipeline**
  - Robust multi-page PDF text extraction via `pypdf` with corruption/encryption guards.
  - Unicode sanitization, whitespace normalization, and bullet formatting.
  - Named entity heuristics (Name, Email, Phone).
  - Extensible software/tech skill dictionary with case-insensitive boundary matching.
  - Section segmentation for Experience and Education.
  - Structured JSON export.

- **Day 2: Job Matching Engine**
  - Automated Job Description requirement parsing (required vs. preferred skills, experience years, education).
  - Canonical skill normalization (`React.js` $\rightarrow$ `React`, `Node JS` $\rightarrow$ `Node.js`, `scikit learn` $\rightarrow$ `Scikit-learn`, `JS` $\rightarrow$ `JavaScript`, `PostgreSQL` $\rightarrow$ `PostgreSQL`).
  - Matched vs. Missing skills categorization.
  - Transparent 0–100 compatibility scoring algorithm:
    - **Skills Match:** 70%
    - **Experience Match:** 20%
    - **Education Match:** 10%
  - Dynamic weight rebalancing when experience/education criteria are unavailable.
  - Explainable recommendation tags: *Strong Match* ($\ge 75$), *Moderate Match* ($50–74$), *Needs Improvement* ($< 50$).

- **Day 3: Candidate Analysis & Report Generation**
  - Factual candidate summary constructed solely from verified resume data (zero hallucinated companies or degrees).
  - Deterministic strength identification based on matched skills, bonus qualifications, tenure, and degree criteria.
  - Clear itemized skill gap analysis tracking required skills vs. presence.
  - In-depth alignment narratives for Experience tenure and Academic qualifications.
  - Rule-based recommendations accompanied by non-hiring disclaimers.
  - Dual-format export: **Structured JSON** and **Formatted Text (.txt)** reports.

---

## Architecture & Data Flow

```text
Parsed Resume (PDF)                 Job Description (Text)
         │                                    │
         ▼                                    ▼
Resume Entity Extraction             Job Requirement Extraction
(Name, Contact, Skills, Exp, Edu)   (Required/Preferred Skills, Exp, Degree)
         │                                    │
         └─────────────────┬──────────────────┘
                           ▼
               Canonical Skill Normalization
                           ▼
               Skill, Exp & Edu Matching
                           ▼
          Weighted Compatibility Scoring (0–100)
             [Skills: 70% | Exp: 20% | Edu: 10%]
                           ▼
               Candidate Analysis Engine
             [Summary | Strengths | Skill Gaps]
                           ▼
            Dual-Format Report Generation
             [JSON Report | Text Document]
                           ▼
                  Streamlit Dashboard
```

---

## Directory Structure

```text
Intelligent-Resume-Analyzer_HiDevs/
├── app.py                     # Streamlit web application (Day 1 + Day 2 + Day 3)
├── requirements.txt           # Minimal dependencies (streamlit, pypdf, pytest)
├── README.md                  # Complete documentation
├── .gitignore                 # Privacy-safe git rules
│
├── utils/
│   ├── __init__.py            # Package exports
│   ├── parser.py              # PDF extraction, entity/section heuristics, JSON saver
│   ├── preprocess.py          # Whitespace, bullet & ligature normalizer
│   ├── skill_extractor.py     # Skill dictionary & normalization engine
│   ├── matcher.py             # JD requirement parsing, matching & weighted scoring
│   └── reporter.py            # Candidate analysis, strengths/gaps & report generation
│
├── data/
│   └── resumes/               # Input resumes (includes sample synthetic PDF)
│
├── outputs/
│   ├── parsed_resumes/        # Saved JSON parsed resumes
│   └── reports/               # Saved candidate analysis reports
│
└── tests/
    ├── __init__.py
    ├── test_parser.py         # Day 1 test suite (11 tests)
    ├── test_matcher.py        # Day 2 test suite (12 tests)
    └── test_reporter.py       # Day 3 test suite (8 tests)
```

---

## Technology Stack

- **Language:** Python 3.14
- **Web UI:** Streamlit
- **Document Processing:** `pypdf`
- **Matching & Analysis:** Python standard library (`re`, `json`, `pathlib`, `typing`, `logging`, `datetime`)
- **Testing:** `pytest`
- **Zero External AI / LLM APIs:** 100% deterministic, explainable, and offline.

---

## Installation & Setup

1. **Activate Virtual Environment** (Windows PowerShell):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

---

## Running the Application

To launch the Streamlit dashboard:

```powershell
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

### Complete Workflow:
1. **Upload Resume**: Select any standard PDF resume (a sample is provided at `data/resumes/sample_synthetic_resume.pdf`).
2. **Click "Parse Resume"**: Review candidate metrics, skills badges, and separated experience/education sections.
3. **Provide Job Description**: Paste a target job description or click **"Load Sample Job Description"**.
4. **Click "Analyze Job Match"**:
   - View Overall Compatibility Score (0–100) and recommendation tier.
   - Inspect breakdown scores: Skills (70%), Experience (20%), Education (10%).
   - Compare Matched Skills (green pills) vs. Missing Skills (red pills).
5. **Review Analysis Report**:
   - Executive Candidate Summary.
   - Verified Strengths list.
   - Itemized Skill Gaps list.
   - Detailed Experience and Education narratives.
6. **Download Reports**:
   - 📥 **Download JSON Report**
   - 📄 **Download Text Report (.txt)**

---

## Running Tests

Run the complete test suite (31 tests across all modules):

```powershell
pytest tests/ -v
```
