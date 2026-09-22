"""
Unit and integration tests for the Job Matching Engine (Day 2).
Covers requirement extraction, skill normalization, 100% match, partial match,
zero match, empty inputs, missing experience, duplicate handling, and scoring.
"""

import pytest
from utils.matcher import (
    extract_job_requirements,
    extract_years_of_experience,
    extract_candidate_experience_years,
    extract_education_level,
    calculate_match_score,
)
from utils.skill_extractor import normalize_skill, normalize_skill_list


def test_skill_normalization():
    """Verify common skill variations normalize to standard canonical names."""
    assert normalize_skill("React.js") == "React"
    assert normalize_skill("react js") == "React"
    assert normalize_skill("Node JS") == "Node.js"
    assert normalize_skill("node.js") == "Node.js"
    assert normalize_skill("scikit learn") == "Scikit-learn"
    assert normalize_skill("sklearn") == "Scikit-learn"
    assert normalize_skill("JS") == "JavaScript"
    assert normalize_skill("javascript") == "JavaScript"
    assert normalize_skill("PostgreSQL") == "PostgreSQL"
    assert normalize_skill("postgres") == "PostgreSQL"
    assert normalize_skill("c++") == "C++"
    assert normalize_skill("python") == "Python"
    assert normalize_skill("") == ""
    assert normalize_skill(None) == ""


def test_normalize_skill_list_deduplication():
    """Verify skill list deduplication and case normalization."""
    skills = ["Python", "python", "REACT.JS", "React", "node js", "Node.js"]
    normalized = normalize_skill_list(skills)
    assert normalized == ["Node.js", "Python", "React"]


def test_extract_job_requirements():
    """Verify structured requirement extraction from a job description text."""
    jd_text = """
    Senior Python Developer
    
    Required Qualifications:
    - 3+ years of software development experience.
    - Bachelor's degree in Computer Science or related field.
    - Proficient in Python, FastAPI, Docker, and PostgreSQL.
    
    Preferred Skills:
    - Experience with AWS and Redis.
    """
    reqs = extract_job_requirements(jd_text)
    assert "Python" in reqs["required_skills"]
    assert "FastAPI" in reqs["required_skills"]
    assert "Docker" in reqs["required_skills"]
    assert "PostgreSQL" in reqs["required_skills"]
    assert "AWS" in reqs["preferred_skills"]
    assert "Redis" in reqs["preferred_skills"]
    assert reqs["experience_requirement"] == 3.0
    assert reqs["education_requirement"] == "Bachelor"


def test_100_percent_skill_match():
    """Verify scoring when candidate has 100% of required skills."""
    resume_data = {
        "skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
        "experience": "5 years of Python engineering experience.",
        "education": "Bachelor of Science in Computer Science",
    }
    job_data = {
        "required_skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
        "preferred_skills": [],
        "experience_requirement": 3.0,
        "education_requirement": "Bachelor",
    }
    result = calculate_match_score(resume_data, job_data)
    assert result["skill_score"] == 100.0
    assert result["experience_score"] == 100.0
    assert result["education_score"] == 100.0
    assert result["overall_score"] == 100.0
    assert result["matched_skills"] == ["Docker", "FastAPI", "PostgreSQL", "Python"]
    assert result["missing_skills"] == []
    assert result["recommendation"] == "Strong Match"


def test_partial_skill_match():
    """Verify scoring and missing skills when candidate matches a subset."""
    resume_data = {
        "skills": ["Python", "SQL", "Git"],
        "experience": "2 years experience.",
        "education": "Bachelor of Technology",
    }
    job_data = {
        "required_skills": ["Python", "SQL", "Docker", "AWS"],
        "preferred_skills": [],
        "experience_requirement": 2.0,
        "education_requirement": "Bachelor",
    }
    result = calculate_match_score(resume_data, job_data)
    # 2 out of 4 skills matched = 50%
    assert result["skill_score"] == 50.0
    assert result["matched_skills"] == ["Python", "SQL"]
    assert result["missing_skills"] == ["AWS", "Docker"]
    # Overall: 50% * 0.70 (35) + 100% * 0.20 (20) + 100% * 0.10 (10) = 65.0
    assert result["overall_score"] == 65.0
    assert result["recommendation"] == "Moderate Match"


def test_zero_skill_match():
    """Verify scoring when candidate has zero overlapping skills."""
    resume_data = {
        "skills": ["HTML", "CSS"],
        "experience": "1 year frontend.",
        "education": "Bachelor of Arts",
    }
    job_data = {
        "required_skills": ["Python", "Docker", "Kubernetes"],
        "preferred_skills": [],
        "experience_requirement": 3.0,
        "education_requirement": "Bachelor",
    }
    result = calculate_match_score(resume_data, job_data)
    assert result["skill_score"] == 0.0
    assert result["matched_skills"] == []
    assert result["missing_skills"] == ["Docker", "Kubernetes", "Python"]
    assert result["overall_score"] < 50.0
    assert result["recommendation"] == "Needs Improvement"


def test_empty_job_description():
    """Verify graceful handling when job description is blank or contains no skills."""
    resume_data = {
        "skills": ["Python", "FastAPI"],
        "experience": "3 years experience",
        "education": "Master of Science",
    }
    job_data = extract_job_requirements("")
    result = calculate_match_score(resume_data, job_data)
    assert result["overall_score"] >= 0.0
    assert isinstance(result["recommendation"], str)
    assert isinstance(result["explanation"], str)


def test_empty_resume():
    """Verify graceful handling when resume data is empty."""
    resume_data = {"skills": [], "experience": "", "education": ""}
    job_data = {
        "required_skills": ["Python", "FastAPI"],
        "preferred_skills": [],
        "experience_requirement": 2.0,
        "education_requirement": "Bachelor",
    }
    result = calculate_match_score(resume_data, job_data)
    assert result["skill_score"] == 0.0
    assert result["matched_skills"] == []
    assert result["missing_skills"] == ["FastAPI", "Python"]
    assert result["overall_score"] < 50.0
    assert result["recommendation"] == "Needs Improvement"


def test_missing_experience_dynamic_reweighting():
    """Verify dynamic re-weighting when resume does not contain parseable experience."""
    resume_data = {
        "skills": ["Python", "FastAPI"],
        "experience": "Contributed to open source projects.",  # No clear years
        "education": "Bachelor in Engineering",
    }
    job_data = {
        "required_skills": ["Python", "FastAPI"],
        "preferred_skills": [],
        "experience_requirement": 3.0,
        "education_requirement": "Bachelor",
    }
    result = calculate_match_score(resume_data, job_data)
    # When experience is unavailable, weights rebalance to 85% skill and 15% education
    # 100% * 0.85 + 100% * 0.15 = 100.0
    assert result["skill_score"] == 100.0
    assert result["education_score"] == 100.0
    assert result["overall_score"] == 100.0
    assert "experience duration was not reliably parseable" in result["explanation"]


def test_case_differences_and_aliases():
    """Verify matching works across casing variations and aliases."""
    resume_data = {
        "skills": ["PYTHON", "react.js", "node js"],
        "experience": "",
        "education": "",
    }
    job_data = {
        "required_skills": ["python", "React", "Node.js"],
        "preferred_skills": [],
        "experience_requirement": None,
        "education_requirement": None,
    }
    result = calculate_match_score(resume_data, job_data)
    assert result["skill_score"] == 100.0
    assert set(result["matched_skills"]) == {"Node.js", "Python", "React"}
    assert result["missing_skills"] == []


def test_experience_extraction_patterns():
    """Verify regex patterns for experience years."""
    assert extract_years_of_experience("3+ years of software experience") == 3.0
    assert extract_years_of_experience("minimum 5 years required") == 5.0
    assert extract_years_of_experience("Requires 2 to 4 years experience") == 2.0
    assert extract_years_of_experience("No experience required") is None


def test_candidate_experience_date_ranges():
    """Verify calculation of experience duration from date spans."""
    exp_text = "Software Engineer (2018 - 2022)\nJunior Developer (2016 - 2018)"
    years = extract_candidate_experience_years(exp_text)
    assert years is not None
    assert years >= 6.0
