# Intelligent Resume Analyzer

An AI-assisted, privacy-first resume screening, job-matching, and candidate analysis application developed in pure Python and Streamlit for the **HiDevs Community Challenge**.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B.svg)](https://streamlit.io)
[![Tests Passing](https://img.shields.io/badge/tests-49%2F49%20passing-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Demo Video](https://img.shields.io/badge/YouTube-Demo%20Video-red.svg)](https://www.youtube.com/watch?v=YOUR_YOUTUBE_DEMO_LINK)

---

### 📌 Project Submission Links
- 📺 **YouTube Demo Video (< 3 min):** [Watch Demo on YouTube](https://youtu.be/_r68ec-ZGn4?si=tihFRwGAf2NnA7qs) *(Paste your uploaded YouTube link here)*
- 💻 **GitHub Repository:** [https://github.com/Nitesh0986/Intelligent-Resume-Analyzer_HiDevs](https://github.com/Nitesh0986/Intelligent-Resume-Analyzer_HiDevs)
- 🚀 **Local Application URL:** `http://localhost:8501`
- 🧪 **Test Suite:** 49/49 Passing (`pytest -v`)
- 👤 **Evaluator Collaboration:** Shared with `deepakchawla`

---

## Overview

**Intelligent Resume Analyzer** is an automated talent assessment engine designed to bridge the gap between candidate resumes and target job descriptions. Operating completely offline and deterministically without external LLM APIs, it extracts structured entities from PDF resumes, normalizes technical skills, scores candidate compatibility using a transparent 3-factor weighting model, and generates comprehensive professional evaluation reports in both structured JSON and formatted text formats.

---

## Problem Statement

Technical recruitment workflows often face substantial bottlenecks:
1. **Manual Ingestion Overhead:** Reviewing multi-page PDF resumes with diverse formatting, non-standard bullets, and irregular typography is time-intensive and error-prone.
2. **Skill Vocabulary Mismatch:** Candidates describe similar proficiencies with different nomenclature (e.g., `React.js` vs. `React`, `Node JS` vs. `Node.js`, `scikit learn` vs. `Scikit-learn`), complicating keyword matching.
3. **Subjective or Opaque Screening:** Traditional automated keyword searchers lack transparency, while commercial LLM screening tools suffer from hallucination, variable scoring, and data privacy vulnerabilities.

---

## Solution

The Intelligent Resume Analyzer provides an explainable, deterministic alternative:
- **Zero External API Dependency:** Runs 100% locally with zero external API calls, safeguarding candidate privacy.
- **Robust Multi-Page PDF Parser:** Extracts text cleanly across pages using `pypdf`, normalizing unicode ligatures, whitespace, and formatting anomalies.
- **Symbol-Safe Canonical Normalization:** Accurately maps programming language symbols (`C`, `C++`, `C#`, `.NET`) and framework variations into canonical terms without false positives.
- **Transparent 70/20/10 Scoring:** Quantifies candidate alignment against configurable criteria with dynamic re-weighting when specific criteria are unavailable.
- **Actionable Reporting:** Distinguishes verified strengths from concrete skill gaps, producing instant downloadable reports.

---

## Features

- **Document Parsing:**
  - Multi-page PDF text extraction with encryption, corruption, and 0-byte guards.
  - Non-destructive text preprocessing (collapsing whitespace, normalizing unicode bullets and quotes).
  - Regex-based contact detail extraction (Email conforming to RFC standards, Indian and international phone numbers).
  - Heuristic candidate name identification filtering out headers, contact blocks, and URLs.
  - Section segmentation for Experience and Education.
- **Requirement & Skill Extraction:**
  - Comprehensive database covering languages, frameworks, databases, cloud, DevOps, and data science/ML.
  - Symbol-safe boundary matching preventing substring clashes (`Java` vs. `JavaScript`, `C` vs. `C++`).
  - Automated job description parsing separating required vs. preferred qualifications, experience tenure, and degree levels.
- **Compatibility Matching:**
  - Categorized breakdown: **Matched Skills** vs. **Missing Skills**.
  - Documented 3-factor weighting:
    - **Skill Match:** 70%
    - **Experience Match:** 20%
    - **Education Match:** 10%
  - Dynamic weight rebalancing when candidate or job tenure/degree criteria are unspecified.
  - Rule-based recommendation tiers: *Strong Match* ($\ge 75$), *Moderate Match* ($50–74$), *Needs Improvement* ($< 50$).
- **Professional Reporting:**
  - Factual candidate summary based exclusively on verified resume evidence.
  - Itemized strength and skill gap identification.
  - In-depth tenure and degree qualification alignment narratives.
  - Dual-format report exports: Structured JSON (`.json`) and Human-Readable Text Document (`.txt`).

---

## Workflow

```text
               ┌──────────────────────────────────────────────┐
               │              Input PDF Resume                │
               └──────────────────────┬───────────────────────┘
                                      │
                                      ▼
               ┌──────────────────────────────────────────────┐
               │    PDF Extraction & Preprocessing (pypdf)     │
               │  - Unicode & ligature normalization          │
               │  - Contact & section heuristics              │
               └──────────────────────┬───────────────────────┘
                                      │
                                      ▼
               ┌──────────────────────────────────────────────┐
               │          Parsed Candidate Profile            │
               │   Name | Email | Phone | Skills | Exp | Edu  │
               └──────────────────────┬───────────────────────┘
                                      │
                 ┌────────────────────┴────────────────────┐
                 │                                         │
                 ▼                                         ▼
   ┌───────────────────────────┐             ┌───────────────────────────┐
   │    Target Job Description │             │ Candidate Extracted Data  │
   │  - Required/Pref Skills   │             │  - Skills Set             │
   │  - Experience Tenure      │             │  - Experience Years       │
   │  - Education Tier         │             │  - Academic Degree        │
   └─────────────┬─────────────┘             └─────────────┬─────────────┘
                 │                                         │
                 └────────────────────┬────────────────────┘
                                      │
                                      ▼
               ┌──────────────────────────────────────────────┐
               │          Job Matching Engine                 │
               │  - Canonical Skill Normalization             │
               │  - Matched vs. Missing Skills                │
               │  - 70 / 20 / 10 Weighted Compatibility Math  │
               └──────────────────────┬───────────────────────┘
                                      │
                                      ▼
               ┌──────────────────────────────────────────────┐
               │     Professional Candidate Analysis          │
               │  - Factual Executive Summary                 │
               │  - Strengths & Itemized Skill Gaps           │
               │  - Experience & Education Alignment          │
               │  - Recommendation (Strong / Moderate / Low)  │
               └──────────────────────┬───────────────────────┘
                                      │
                                      ▼
               ┌──────────────────────────────────────────────┐
               │           Dual-Format Export                 │
               │  - Download JSON Report (.json)              │
               │  - Download Human-Readable Report (.txt)     │
               └──────────────────────────────────────────────┘
```

---

## Tech Stack

- **Core Language:** Python 3.14
- **User Interface:** Streamlit
- **PDF Extraction Engine:** `pypdf` (v5.0+)
- **Text & Rule Processing:** Python standard library (`re`, `json`, `pathlib`, `typing`, `logging`, `datetime`, `unicodedata`)
- **Automated Testing:** `pytest` (v8.0+)
- **Third-Party AI / LLMs:** None (100% deterministic, explainable, and private)

---

## Project Structure

```text
Intelligent-Resume-Analyzer_HiDevs/
│
├── app.py                     # Streamlit web application & single-screen UI orchestration
├── requirements.txt           # Minimal production dependencies (streamlit, pypdf, pytest)
├── README.md                  # Comprehensive project documentation
├── .gitignore                 # Privacy rules preventing tracking of resumes or reports
│
├── utils/                     # Modular backend business logic
│   ├── __init__.py            # Package exports
│   ├── parser.py              # PDF extraction, entity heuristics, and JSON saver
│   ├── preprocess.py          # Whitespace, ligature, quote, and bullet normalizer
│   ├── skill_extractor.py     # Extensible skills dictionary & canonical normalizer
│   ├── matcher.py             # JD requirement extraction & weighted scoring algorithm
│   └── reporter.py            # Factual summary, strengths/gaps & dual-format report builders
│
├── data/
│   └── resumes/               # Directory for input resumes (with .gitkeep and test PDF)
│
├── outputs/                   # Auto-saved outputs (git-ignored for privacy)
│   ├── parsed_resumes/        # Parsed resume JSON files
│   └── reports/               # Generated candidate analysis JSON reports
│
└── tests/                     # Test harness (49 tests, 100% passing)
    ├── __init__.py
    ├── test_parser.py         # Day 1 extraction and entity tests (11 tests)
    ├── test_matcher.py        # Day 2 normalization and matching tests (13 tests)
    ├── test_reporter.py       # Day 3 analysis and reporting tests (9 tests)
    └── test_final_qa.py       # Day 5 comprehensive 12-scenario and boundary tests (16 tests)
```

---

## Installation

### Prerequisites
- Python 3.10 to 3.14
- Git

### 1. Clone the Repository
```powershell
git clone https://github.com/Nitesh0986/Intelligent-Resume-Analyzer_HiDevs.git
cd Intelligent-Resume-Analyzer_HiDevs
```

### 2. Set Up Virtual Environment (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## Usage

### Launching the Dashboard
From the root directory with the virtual environment activated, run:
```powershell
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### Step-by-Step Walkthrough
1. **Upload Resume:** Click **Browse files** and upload a candidate PDF resume (or use `data/resumes/sample_synthetic_resume.pdf`).
2. **Analyze Resume:** Click the primary **"Analyze Resume"** button. Review candidate contact information, verified skills, and extracted background sections.
3. **Target Job Description:** Enter or paste the job description, or click **"📝 Load Sample Job Description"** for immediate demo data.
4. **Analyze Match:** Click the primary **"Analyze Match"** button.
5. **Inspect Results:**
   - Review the **Overall Match Score** gauge ($0\text{--}100$) and Recommendation badge (*Strong Match*, *Moderate Match*, *Needs Improvement*).
   - Check dimension breakdowns: Skill Score (70%), Experience Score (20%), Education Score (10%).
   - Review **Matched Skills** (green badges) vs. **Missing Skills** (red badges).
   - Review **Strengths**, **Skill Gaps**, and narrative analysis.
6. **Export Assessment:**
   - Click **📥 Download JSON** for structured machine-readable analysis.
   - Click **📄 Download Report** for a formatted plaintext document.

---

## Matching Methodology

Compatibility is computed using a transparent, documented arithmetic formula:

$$\text{Overall Score} = (\text{Skill Score} \times 0.70) + (\text{Experience Score} \times 0.20) + (\text{Education Score} \times 0.10)$$

### 1. Technical Skill Score (70%)
$$\text{Base Skill Score} = \left( \frac{|\text{Candidate Skills} \cap \text{Required Skills}|}{|\text{Required Skills}|} \right) \times 100$$
- Preferred / Bonus qualifications present on the resume contribute an additional incentive of up to 5%, capped at 100%.

### 2. Experience Alignment Score (20%)
- If the job description requires $Y$ years and the candidate demonstrates $C$ years:
  - If $C \ge Y \implies 100\%$
  - If $C < Y \implies \left(\frac{C}{Y}\right) \times 100\%$
- If the job description does not specify minimum tenure, this factor is treated neutrally (100%).

### 3. Education Qualification Score (10%)
- Academic degrees are evaluated hierarchically:
  $$\text{PhD (5)} > \text{Master (4)} > \text{Bachelor (3)} > \text{Associate (2)} > \text{High School (1)}$$
- Candidates meeting or exceeding the requested degree tier receive 100%.

### 4. Dynamic Re-weighting Fallback
If candidate experience tenure or academic credentials cannot be verified from the document, the algorithm dynamically re-weights between evaluable dimensions (e.g., 85% Skills / 15% Education) so the score remains fair and strictly within $[0, 100]$.

> **Notice:** The match score is an algorithmic resume-to-job compatibility index based on configured matching criteria. It does not constitute a hiring decision or hiring probability.

---

## Error Handling

The application includes defensive input handling across all layers:
- **Empty / 0-Byte PDF Files:** Displays a clear warning preventing zero-division errors.
- **Corrupted / Invalid PDFs:** Gracefully caught via `pypdf.errors.PdfReadError` without exposing Python tracebacks.
- **Scanned / Image-Only PDFs:** Informs the user when no text layer is extractable.
- **Empty / Too-Short Job Descriptions:** Rejects inputs under 30 characters before executing matching heuristics.
- **Missing Sections:** Gracefully continues extraction when candidates omit email, phone, education, or work history.
- **Division by Zero:** Guarded against jobs with zero required skills or zero experience requirements.

---

## Example

### Input Candidate Data
- **Name:** Alex Smith
- **Skills:** Python, FastAPI, Docker, PostgreSQL, AWS, Git
- **Experience:** 4 years backend software engineering (2020 - 2024)
- **Education:** Bachelor of Technology in Computer Science

### Target Job Requirements
- **Required Skills:** Python, FastAPI, Docker, PostgreSQL
- **Preferred Skills:** AWS, Kubernetes
- **Required Experience:** 3+ years
- **Required Degree:** Bachelor's degree

### Output Assessment
- **Overall Match Score:** `100.0 / 100`
- **Recommendation:** `Strong Match`
- **Matched Skills:** `Docker`, `FastAPI`, `PostgreSQL`, `Python`
- **Missing Skills:** `None`
- **Strengths:**
  - Demonstrated proficiency in key required skills: Docker, FastAPI, PostgreSQL, Python.
  - Offers desirable preferred qualifications: AWS.
  - Meets or exceeds the required tenure (~4 years documented vs 3 years required).
  - Meets academic credential standards with a verified Bachelor degree.
- **Skill Gaps:** `All primary required skills are satisfied with no detected gaps.`

---

## Screenshots

*(To capture screenshots during local execution, navigate the single-screen application and save screenshots to an `assets/` directory if desired).*

| Screen Section | Description |
|---|---|
| **Header & Resume Ingestion** | PDF upload widget with instant parsing status and profile cards. |
| **Target Job Matching** | Side-by-side job description input with sample load action. |
| **Compatibility Assessment** | Visual score gauge, dimensional breakdown metrics, and matched/missing skill pills. |
| **Analysis & Report Downloads** | Factual summary, strengths/gaps cards, and dual download buttons. |

---

## Demo

### 📺 3-Minute Project Demo Video
Watch the complete application walkthrough demonstration on YouTube:

👉 **[Watch Project Demo Video on YouTube](https://www.youtube.com/watch?v=YOUR_YOUTUBE_DEMO_LINK)**

> *Note for Evaluators: If viewing offline, you can also run the application locally in one command (`streamlit run app.py`) or inspect the 3-minute video link above.*

### 3-Minute Video Presentation Structure
- **0:00 – 0:20 | Introduction:** Problem statement, privacy-first offline architecture, zero-LLM deterministic design.
- **0:20 – 0:50 | Resume Ingestion:** Uploading a PDF resume and instant entity extraction (`pypdf`).
- **0:50 – 1:20 | Candidate Information:** Reviewing candidate profile, contact details, identified skills, and background sections.
- **1:20 – 1:50 | Job Description Matching:** Loading target job criteria (preset or custom) and triggering match evaluation.
- **1:50 – 2:20 | Compatibility Dashboard:** Explaining the 70/20/10 score breakdown, matched vs. missing skills, and dynamic re-weighting.
- **2:20 – 2:45 | Analysis & Reports:** Reviewing factual summary, strengths, skill gaps, and testing the JSON and TXT download buttons.
- **2:45 – 3:00 | Quality & Wrap-up:** Demonstrating test coverage (49/49 passing) and Git repository cleanliness.

---

## Limitations

1. **Scanned / Image-Only PDFs:** Relies on embedded text streams. Resumes submitted as scanned bitmap images require optical character recognition (OCR), which is not bundled to maintain a lightweight runtime.
2. **Heuristic Header Detection:** Candidate name extraction utilizes top-section structural patterns; atypical layouts (such as multi-column sidebars with names in the footer) may not detect the name accurately.
3. **Dictionary-Bound Skill Recognition:** While the skill dictionary contains 150+ core software proficiencies and normalizes aliases, niche technologies outside the database are not captured unless added to `SKILLS_DATABASE`.

---

## Future Improvements

- **Tesseract OCR Integration:** Optional OCR fallback for scanned resume images.
- **Multi-Resume Batch Ranking:** Uploading a folder of resumes to rank candidate compatibility in a comparative table.
- **Custom Skill Dictionary Upload:** Allowing recruiters to upload domain-specific skill taxonomy files (e.g., finance, healthcare, legal).
- **Direct PDF Export:** Adding native `.pdf` generation alongside `.json` and `.txt`.

---

## Author & Submission Details

Developed for the **HiDevs Community Challenge (Project ID: 88)**.
- **Project Name:** `intelligent_resume_analyzer_hidevs` / `Intelligent-Resume-Analyzer_HiDevs`
- **GitHub Repository:** [https://github.com/Nitesh0986/Intelligent-Resume-Analyzer_HiDevs](https://github.com/Nitesh0986/Intelligent-Resume-Analyzer_HiDevs)
- **Author:** Nitesh ([@Nitesh0986](https://github.com/Nitesh0986))
- **Reviewer / Collaborator Access:** Shared with `deepakchawla`
- **Submission Portal:** [HiDevs Submission Portal](https://app.hidevs.xyz/projects/88?tab=submission)
- **License:** Open for academic and evaluation review.

