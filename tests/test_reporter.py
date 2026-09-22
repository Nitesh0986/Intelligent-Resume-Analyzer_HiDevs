"""
Unit and integration tests for Candidate Analysis and Report Generation (Day 3).
Tests complete candidate evaluation, missing skills, missing education,
missing experience, empty inputs, malformed data, and JSON / text export.
"""

import json
import pytest

from utils.reporter import (
    generate_candidate_summary,
    identify_strengths,
    identify_skill_gaps,
    analyze_experience_alignment,
    analyze_education_alignment,
    generate_candidate_analysis,
    generate_human_readable_report,
    save_candidate_report,
)
from utils.matcher import calculate_match_score


@pytest.fixture
def sample_complete_candidate():
    return {
        "name": "Alex Smith",
        "email": "alex.smith@example.com",
        "phone": "+91 9876543210",
        "skills": ["Python", "FastAPI", "Docker", "PostgreSQL", "Git", "AWS"],
        "experience": "Senior Software Engineer (2020 - 2024)\n- Developed microservices with Python and FastAPI.",
        "education": "Bachelor of Technology in Computer Science (2016 - 2020)",
    }


@pytest.fixture
def sample_job_reqs():
    return {
        "required_skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
        "preferred_skills": ["AWS"],
        "experience_requirement": 3.0,
        "education_requirement": "Bachelor",
    }


def test_complete_candidate_analysis(sample_complete_candidate, sample_job_reqs):
    match_eval = calculate_match_score(sample_complete_candidate, sample_job_reqs)
    analysis = generate_candidate_analysis(sample_complete_candidate, sample_job_reqs, match_eval)

    assert "Alex Smith" in analysis["candidate_summary"]
    assert "Python" in analysis["candidate_summary"]
    assert analysis["overall_score"] == 100.0
    assert analysis["matched_skills"] == ["Docker", "FastAPI", "PostgreSQL", "Python"]
    assert analysis["missing_skills"] == []
    assert len(analysis["strengths"]) > 0
    assert "All primary required skills are satisfied" in analysis["skill_gaps"][0]
    assert "satisfying the target requirement of 3+" in analysis["experience_analysis"]
    assert "fulfills or exceeds" in analysis["education_analysis"]
    assert "Strong Match" in analysis["recommendation"]
    assert "generated_at" in analysis


def test_candidate_with_missing_skills(sample_job_reqs):
    partial_candidate = {
        "name": "Jordan Lee",
        "email": "jordan@example.com",
        "skills": ["Python", "Git"],
        "experience": "3 years software engineer.",
        "education": "Bachelor of Science",
    }
    match_eval = calculate_match_score(partial_candidate, sample_job_reqs)
    analysis = generate_candidate_analysis(partial_candidate, sample_job_reqs, match_eval)

    assert "Python" in analysis["matched_skills"]
    assert "Docker" in analysis["missing_skills"]
    assert "FastAPI" in analysis["missing_skills"]
    assert "PostgreSQL" in analysis["missing_skills"]
    assert any("Docker" in gap for gap in analysis["skill_gaps"])
    assert any("PostgreSQL" in gap for gap in analysis["skill_gaps"])


def test_candidate_with_missing_education(sample_job_reqs):
    no_edu_candidate = {
        "name": "Sam Developer",
        "email": "sam@dev.org",
        "skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
        "experience": "4 years backend engineering.",
        "education": "",  # Missing education
    }
    match_eval = calculate_match_score(no_edu_candidate, sample_job_reqs)
    analysis = generate_candidate_analysis(no_edu_candidate, sample_job_reqs, match_eval)

    # Should not fabricate a degree
    assert "No specific degree level was explicitly identified" in analysis["candidate_summary"]
    assert "does not explicitly mention a recognized academic degree" in analysis["education_analysis"]


def test_candidate_with_missing_experience(sample_job_reqs):
    no_exp_candidate = {
        "name": "Taylor Fresh",
        "email": "taylor@fresh.edu",
        "skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
        "experience": "",  # Missing experience section
        "education": "Bachelor of Technology",
    }
    match_eval = calculate_match_score(no_exp_candidate, sample_job_reqs)
    analysis = generate_candidate_analysis(no_exp_candidate, sample_job_reqs, match_eval)

    assert "No distinct work experience history was identified" in analysis["candidate_summary"]
    assert "could not be reliably quantified" in analysis["experience_analysis"]


def test_empty_and_none_data():
    empty_resume = {}
    empty_job = {}
    empty_match = {}

    analysis = generate_candidate_analysis(empty_resume, empty_job, empty_match)
    assert isinstance(analysis["candidate_summary"], str)
    assert isinstance(analysis["strengths"], list)
    assert isinstance(analysis["skill_gaps"], list)
    assert isinstance(analysis["experience_analysis"], str)
    assert isinstance(analysis["education_analysis"], str)


def test_malformed_data():
    malformed_resume = {"skills": "not_a_list", "experience": 12345, "education": None}
    malformed_job = {"required_skills": None, "experience_requirement": "invalid"}
    malformed_match = {"overall_score": "NaN", "matched_skills": None}

    # Must handle gracefully without crashing
    analysis = generate_candidate_analysis(malformed_resume, malformed_job, malformed_match)
    assert isinstance(analysis, dict)
    assert "generated_at" in analysis


def test_human_readable_report_format(sample_complete_candidate, sample_job_reqs):
    match_eval = calculate_match_score(sample_complete_candidate, sample_job_reqs)
    analysis = generate_candidate_analysis(sample_complete_candidate, sample_job_reqs, match_eval)
    report_text = generate_human_readable_report(analysis, sample_complete_candidate)

    assert "INTELLIGENT RESUME ANALYZER" in report_text
    assert "Candidate: Alex Smith" in report_text
    assert "alex.smith@example.com" in report_text
    assert "OVERALL COMPATIBILITY SCORE:" in report_text
    assert "CANDIDATE SUMMARY" in report_text
    assert "MATCHED SKILLS" in report_text
    assert "MISSING SKILLS" in report_text
    assert "STRENGTHS" in report_text
    assert "SKILL GAPS" in report_text
    assert "EXPERIENCE ANALYSIS" in report_text
    assert "EDUCATION ANALYSIS" in report_text
    assert "DISCLAIMER:" in report_text


def test_save_candidate_report(tmp_path, sample_complete_candidate, sample_job_reqs):
    match_eval = calculate_match_score(sample_complete_candidate, sample_job_reqs)
    analysis = generate_candidate_analysis(sample_complete_candidate, sample_job_reqs, match_eval)

    saved_file = save_candidate_report(analysis, output_dir=tmp_path)
    assert saved_file.exists()
    assert saved_file.suffix == ".json"

    with open(saved_file, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    assert loaded["overall_score"] == 100.0
    assert loaded["matched_skills"] == ["Docker", "FastAPI", "PostgreSQL", "Python"]


def test_standalone_reporter_helpers(sample_complete_candidate, sample_job_reqs):
    match_eval = calculate_match_score(sample_complete_candidate, sample_job_reqs)
    
    summary = generate_candidate_summary(sample_complete_candidate)
    assert "Alex Smith" in summary
    
    strengths = identify_strengths(sample_complete_candidate, sample_job_reqs, match_eval)
    assert len(strengths) > 0
    assert any("Docker" in s for s in strengths)
    
    gaps = identify_skill_gaps(sample_job_reqs, match_eval)
    assert len(gaps) == 1
    assert "All primary required skills are satisfied" in gaps[0]
    
    exp_an = analyze_experience_alignment(sample_complete_candidate, sample_job_reqs, match_eval)
    assert "satisfying the target requirement" in exp_an
    
    edu_an = analyze_education_alignment(sample_complete_candidate, sample_job_reqs, match_eval)
    assert "fulfills or exceeds" in edu_an
