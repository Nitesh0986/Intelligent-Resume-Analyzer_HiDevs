# Intelligent Resume Analyzer (HiDevs Challenge)

An AI-assisted resume parsing and candidate analysis engine developed for the HiDevs Intelligent Resume Analyzer project.

## Day 1: Resume Parsing Pipeline

The Day 1 implementation establishes a robust, deterministic parsing pipeline that converts raw PDF resumes into structured JSON models and displays them in an interactive Streamlit UI.

### Architecture & Pipeline Flow

```
PDF Resume
    ↓
PDF Text Extraction (pypdf with error/encryption handling)
    ↓
Text Sanitization & Normalization (utils/preprocess.py)
    ↓
Entity & Section Extraction (utils/parser.py, utils/skill_extractor.py)
    ├── Candidate Name
    ├── Email
    ├── Phone
    ├── Technical Skills
    ├── Education
    └── Experience
    ↓
Structured Python Dictionary
    ↓
JSON Export (outputs/parsed_resumes/)
    ↓
Streamlit Preview UI (app.py)
```

---

## Directory Structure

```text
Intelligent-Resume-Analyzer_HiDevs/
├── app.py                     # Streamlit web application
├── requirements.txt           # Minimal Day 1 dependencies (pypdf, streamlit, pytest)
├── README.md                  # Project documentation & runbook
├── .gitignore                 # Configured for privacy and clean Git history
│
├── utils/
│   ├── __init__.py            # Utility package exports
│   ├── parser.py              # PDF extraction, entity/section heuristics, JSON saver
│   ├── preprocess.py          # Whitespace, bullet, ligature & quote normalizer
│   └── skill_extractor.py     # Extensible skills database & symbol-safe regex matcher
│
├── data/
│   └── resumes/               # Directory for input resumes (with sample test PDF)
│
├── outputs/
│   └── parsed_resumes/        # Directory for automatically saved JSON output files
│
└── tests/
    ├── __init__.py
    └── test_parser.py         # Pytest suite testing extraction, boundaries & errors
```

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

To launch the interactive Streamlit user interface:

```powershell
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

### Using the App:
1. Upload any standard PDF resume (a sample is provided at `data/resumes/sample_synthetic_resume.pdf`).
2. Click **🚀 Analyze Resume**.
3. View the candidate's profile metrics (Name, Email, Phone), technical skills badges, and separated Experience and Education sections.
4. Download the generated structured JSON file or view it directly in the UI. Parsed results are automatically saved to `outputs/parsed_resumes/`.

---

## Running Tests

Run the automated test suite with pytest:

```powershell
pytest tests/test_parser.py -v
```
