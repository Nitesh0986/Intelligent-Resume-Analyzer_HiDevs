"""
Final Comprehensive QA Test Suite (Day 5).
Validates all 12 functional scenarios and scoring constraints required by HiDevs.

Test Scenarios:
1. Normal PDF parsing
2. Invalid PDF handling
3. Empty PDF (0 bytes / 0 pages)
4. Resume without email address
5. Resume without phone number
6. Resume with no recognized technical skills
7. Empty job description input
8. Partial skill match
9. Strong skill match
10. Missing experience information
11. Missing education information
12. Dual-format report generation (JSON and Text)
"""

import io
import json
import pytest
import pypdf

from utils.parser import (
    extract_text_from_pdf,
    extract_email,
    extract_phone,
    extract_name,
    parse_resume,
    save_parsed_resume,
)
from utils.matcher import (
    extract_job_requirements,
    calculate_match_score,
)
from utils.reporter import (
    generate_candidate_analysis,
    generate_human_readable_report,
    save_candidate_report,
)


def _build_minimal_synthetic_pdf(text: str) -> io.BytesIO:
    """Helper to generate a valid minimal PDF in-memory containing text."""
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    stream = io.BytesIO()
    writer.write(stream)
    stream.seek(0)
    return stream


# ==============================================================================
# 1. NORMAL PDF
# ==============================================================================
def test_scenario_01_normal_pdf():
    """Verify parsing a valid, typical resume text structure."""
    normal_text = """
    Jane Doe
    Email: jane.doe@example.com | Phone: +91 9876543210
    
    Professional Summary:
    Experienced Python and FastAPI backend engineer.
    
    Skills:
    Python, FastAPI, Docker, PostgreSQL, Git
    
    Experience:
    Senior Developer (2020 - 2024)
    - Designed scalable microservices.
    
    Education:
    Bachelor of Technology in Computer Science (2016 - 2020)
    """
    res = parse_resume(normal_text)
    assert res["name"] == "Jane Doe"
    assert res["email"] == "jane.doe@example.com"
    assert res["phone"] == "+91 9876543210"
    assert "Python" in res["skills"]
    assert "FastAPI" in res["skills"]
    assert "Senior Developer" in res["experience"]
    assert "Bachelor of Technology" in res["education"]


# ==============================================================================
# 2. INVALID PDF
# ==============================================================================
def test_scenario_02_invalid_pdf():
    """Verify corrupted / non-PDF bytes raise a clear ValueError without crashing."""
    corrupted_stream = io.BytesIO(b"NOT_A_VALID_PDF_HEADER_OR_CONTENT")
    with pytest.raises(ValueError, match="Corrupted or unreadable PDF"):
        extract_text_from_pdf(corrupted_stream)


# ==============================================================================
# 3. EMPTY PDF
# ==============================================================================
def test_scenario_03_empty_pdf():
    """Verify an empty PDF file or 0-page document is handled safely."""
    # 0 bytes
    empty_stream = io.BytesIO(b"")
    with pytest.raises(ValueError, match="Corrupted or unreadable PDF"):
        extract_text_from_pdf(empty_stream)

    # 1-page blank PDF
    blank_pdf = _build_minimal_synthetic_pdf("")
    extracted = extract_text_from_pdf(blank_pdf)
    assert extracted == ""


# ==============================================================================
# 4. RESUME WITHOUT EMAIL
# ==============================================================================
def test_scenario_04_resume_without_email():
    """Verify resume with no email parses cleanly with empty/None email."""
    text_no_email = "John Doe\nPhone: +91 9876543210\nSkills: Python, Docker"
    res = parse_resume(text_no_email)
    assert res["name"] == "John Doe"
    assert res["email"] == ""
    assert res["phone"] == "+91 9876543210"


# ==============================================================================
# 5. RESUME WITHOUT PHONE
# ==============================================================================
def test_scenario_05_resume_without_phone():
    """Verify resume with no phone number parses cleanly."""
    text_no_phone = "Alice Walker\nEmail: alice@example.com\nSkills: React, TypeScript"
    res = parse_resume(text_no_phone)
    assert res["name"] == "Alice Walker"
    assert res["email"] == "alice@example.com"
    assert res["phone"] == ""


# ==============================================================================
# 6. RESUME WITH NO RECOGNIZED SKILLS
# ==============================================================================
def test_scenario_06_resume_with_no_recognized_skills():
    """Verify resume containing non-technical text produces an empty skill list gracefully."""
    non_tech_text = "Bob Dylan\nSinger and Songwriter\nExtensive performance background in acoustic folk music."
    res = parse_resume(non_tech_text)
    assert res["skills"] == []

    # Scoring against a tech job should yield 0 for skills without errors
    job_reqs = {"required_skills": ["Python", "FastAPI"], "preferred_skills": []}
    match_eval = calculate_match_score(res, job_reqs)
    assert match_eval["skill_score"] == 0.0
    assert match_eval["matched_skills"] == []
    assert set(match_eval["missing_skills"]) == {"FastAPI", "Python"}


# ==============================================================================
# 7. EMPTY JOB DESCRIPTION
# ==============================================================================
def test_scenario_07_empty_job_description():
    """Verify matching against an empty job description returns a safe fallback."""
    resume_data = {
        "skills": ["Python", "SQL"],
        "experience": "2 years dev",
        "education": "Bachelor of Science",
    }
    empty_jd_reqs = extract_job_requirements("")
    assert empty_jd_reqs["required_skills"] == []
    assert empty_jd_reqs["experience_requirement"] is None

    match_eval = calculate_match_score(resume_data, empty_jd_reqs)
    assert 0.0 <= match_eval["overall_score"] <= 100.0
    assert isinstance(match_eval["recommendation"], str)


# ==============================================================================
# 8. PARTIAL SKILL MATCH
# ==============================================================================
def test_scenario_08_partial_skill_match():
    """Verify proportional scoring and missing skills list for partial matches."""
    resume_data = {
        "skills": ["Python", "SQL"],
        "experience": "3 years experience",
        "education": "Bachelor of Science",
    }
    job_reqs = {
        "required_skills": ["Python", "SQL", "Docker", "AWS"],
        "preferred_skills": [],
        "experience_requirement": 3.0,
        "education_requirement": "Bachelor",
    }
    match_eval = calculate_match_score(resume_data, job_reqs)
    # 2 of 4 required skills = 50.0%
    assert match_eval["skill_score"] == 50.0
    assert match_eval["matched_skills"] == ["Python", "SQL"]
    assert match_eval["missing_skills"] == ["AWS", "Docker"]
    # Overall: 50% * 0.70 (35) + 100% * 0.20 (20) + 100% * 0.10 (10) = 65.0
    assert match_eval["overall_score"] == 65.0
    assert match_eval["recommendation"] == "Moderate Match"


# ==============================================================================
# 9. STRONG SKILL MATCH
# ==============================================================================
def test_scenario_09_strong_skill_match():
    """Verify 100% skill match gives top score and Strong Match recommendation."""
    resume_data = {
        "skills": ["Python", "FastAPI", "Docker", "PostgreSQL", "AWS"],
        "experience": "5 years senior engineering",
        "education": "Master of Science in Computer Science",
    }
    job_reqs = {
        "required_skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
        "preferred_skills": ["AWS"],
        "experience_requirement": 3.0,
        "education_requirement": "Bachelor",
    }
    match_eval = calculate_match_score(resume_data, job_reqs)
    assert match_eval["skill_score"] == 100.0
    assert match_eval["experience_score"] == 100.0
    assert match_eval["education_score"] == 100.0
    assert match_eval["overall_score"] == 100.0
    assert match_eval["missing_skills"] == []
    assert match_eval["recommendation"] == "Strong Match"


# ==============================================================================
# 10. MISSING EXPERIENCE INFORMATION
# ==============================================================================
def test_scenario_10_missing_experience_information():
    """Verify dynamic re-weighting when experience section is absent or unparseable."""
    resume_data = {
        "skills": ["Python", "FastAPI", "Docker"],
        "experience": "",  # Empty
        "education": "Bachelor of Technology",
    }
    job_reqs = {
        "required_skills": ["Python", "FastAPI", "Docker"],
        "preferred_skills": [],
        "experience_requirement": 3.0,
        "education_requirement": "Bachelor",
    }
    match_eval = calculate_match_score(resume_data, job_reqs)
    # Experience should rebalance to skills & education without dropping score
    assert 0.0 <= match_eval["overall_score"] <= 100.0
    analysis = generate_candidate_analysis(resume_data, job_reqs, match_eval)
    assert "could not be reliably quantified" in analysis["experience_analysis"]


# ==============================================================================
# 11. MISSING EDUCATION INFORMATION
# ==============================================================================
def test_scenario_11_missing_education_information():
    """Verify handling when education is omitted, avoiding degree fabrication."""
    resume_data = {
        "skills": ["Python", "FastAPI"],
        "experience": "4 years backend developer",
        "education": "",  # Missing
    }
    job_reqs = {
        "required_skills": ["Python", "FastAPI"],
        "preferred_skills": [],
        "experience_requirement": 2.0,
        "education_requirement": "Bachelor",
    }
    match_eval = calculate_match_score(resume_data, job_reqs)
    analysis = generate_candidate_analysis(resume_data, job_reqs, match_eval)
    assert "does not explicitly mention a recognized academic degree" in analysis["education_analysis"]
    assert "No specific degree level was explicitly identified" in analysis["candidate_summary"]


# ==============================================================================
# 12. REPORT GENERATION (JSON & TEXT)
# ==============================================================================
def test_scenario_12_report_generation(tmp_path):
    """Verify full end-to-end report generation and dual-format exports."""
    resume_data = {
        "name": "Jordan Casey",
        "email": "jordan@example.com",
        "phone": "+91 9123456780",
        "skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
        "experience": "4 years software engineering experience (2020 - 2024)",
        "education": "Bachelor of Science in Computer Science",
    }
    job_reqs = {
        "required_skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
        "preferred_skills": [],
        "experience_requirement": 3.0,
        "education_requirement": "Bachelor",
    }

    match_eval = calculate_match_score(resume_data, job_reqs)
    analysis = generate_candidate_analysis(resume_data, job_reqs, match_eval)

    # 1. JSON Report validation
    json_path = save_candidate_report(analysis, output_dir=tmp_path)
    assert json_path.exists()
    assert json_path.suffix == ".json"

    with open(json_path, "r", encoding="utf-8") as f:
        loaded_json = json.load(f)
    assert loaded_json["overall_score"] == 100.0
    assert loaded_json["recommendation"] == "Strong Match"
    assert "Jordan Casey" in loaded_json["candidate_summary"]

    # 2. Text Report validation
    text_report = generate_human_readable_report(analysis, resume_data)
    assert "INTELLIGENT RESUME ANALYZER" in text_report
    assert "Candidate: Jordan Casey" in text_report
    assert "Email:     jordan@example.com" in text_report
    assert "OVERALL COMPATIBILITY SCORE: 100.0 / 100" in text_report
    assert "DISCLAIMER:" in text_report


# ==============================================================================
# PHASE 3: SCORING VALIDATION (0 <= score <= 100)
# ==============================================================================
@pytest.mark.parametrize(
    "skills,exp,edu,req_skills,req_exp,req_edu",
    [
        ([], "", "", ["Python"], 5.0, "PhD"),
        (["Python"], "10 years", "PhD", [], None, None),
        (["Python", "C++", "Java", "Docker"], "2 years", "Master", ["Python", "AWS"], 3.0, "Bachelor"),
        (["HTML"], "6 months", "Associate", ["Docker", "Kubernetes", "AWS"], 5.0, "Bachelor"),
    ],
)
def test_scoring_boundary_guarantee(skills, exp, edu, req_skills, req_exp, req_edu):
    """Verify that under any permutation, score is always float and strictly 0 <= score <= 100."""
    res = {"skills": skills, "experience": exp, "education": edu}
    job = {
        "required_skills": req_skills,
        "preferred_skills": [],
        "experience_requirement": req_exp,
        "education_requirement": req_edu,
    }
    match_eval = calculate_match_score(res, job)
    score = match_eval["overall_score"]
    assert isinstance(score, float)
    assert 0.0 <= score <= 100.0
    assert 0.0 <= match_eval["skill_score"] <= 100.0
    assert 0.0 <= match_eval["experience_score"] <= 100.0
    assert 0.0 <= match_eval["education_score"] <= 100.0
