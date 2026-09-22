"""
Job Matching Engine for Intelligent Resume Analyzer.

Provides deterministic, explainable resume-to-job description matching,
including requirement extraction, skill comparison, experience and education
alignment, and weighted compatibility scoring.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .preprocess import clean_text
from .skill_extractor import extract_skills, normalize_skill, normalize_skill_list

# Documented Weight Distribution for Overall Score
WEIGHT_SKILLS = 0.70      # 70% Skill Match
WEIGHT_EXPERIENCE = 0.20  # 20% Experience Alignment
WEIGHT_EDUCATION = 0.10   # 10% Education Qualifications

# Academic degree tier hierarchy
DEGREE_TIERS = {
    "High School": 1,
    "Associate": 2,
    "Diploma": 2,
    "Bachelor": 3,
    "Master": 4,
    "PhD": 5,
}


def extract_years_of_experience(text: str) -> Optional[float]:
    """
    Extract required or mentioned years of experience from text.

    Supports expressions such as:
    - '2+ years', '3 years of experience', 'minimum 5 years', '3-5 years'

    Args:
        text: Normalized text from job description or resume.

    Returns:
        Float representing minimum years of experience, or None if not detected.
    """
    if not text:
        return None

    # Pattern for explicit experience statements
    patterns = [
        # 'minimum 5 years', 'at least 3 years'
        r"(?:minimum|at\s*least)\s*(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)",
        # '3+ years', '3-5 years', '5 years of experience'
        r"(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:to|-)?\s*(?:\d+)?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+(?:relevant|work|industry|software)?\s*experience)?",
    ]

    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            try:
                years = float(match.group(1))
                if 0 < years <= 40:  # Plausible career range
                    return years
            except (ValueError, IndexError):
                continue

    return None


def extract_candidate_experience_years(text: str) -> Optional[float]:
    """
    Estimate total candidate work experience in years from resume experience text.

    Combines explicit mentions ('X years experience') and date ranges ('2019 - 2023').

    Args:
        text: Text from the resume's experience section.

    Returns:
        Estimated years of experience, or None if not reliably found.
    """
    if not text:
        return None

    # First check explicit mention
    explicit_years = extract_years_of_experience(text)
    if explicit_years is not None:
        return explicit_years

    # Scan for date ranges like 2018 - 2022, 2021 - Present
    current_year = datetime.now().year
    range_pattern = r"(20\d{2}|19\d{2})\s*(?:-|to|–|—)\s*(20\d{2}|present|current|now)"
    matches = re.findall(range_pattern, text, re.IGNORECASE)

    if matches:
        spans: List[Tuple[int, int]] = []
        for start_str, end_str in matches:
            try:
                start_yr = int(start_str)
                if end_str.lower() in ("present", "current", "now"):
                    end_yr = current_year
                else:
                    end_yr = int(end_str)

                if start_yr <= end_yr:
                    spans.append((start_yr, end_yr))
            except ValueError:
                continue

        if spans:
            # Merge overlapping year intervals
            spans.sort(key=lambda x: x[0])
            merged: List[Tuple[int, int]] = [spans[0]]
            for current in spans[1:]:
                prev_start, prev_end = merged[-1]
                if current[0] <= prev_end:
                    merged[-1] = (prev_start, max(prev_end, current[1]))
                else:
                    merged.append(current)

            total_years = sum(end - start for start, end in merged)
            # Default single-year tenure if start == end
            if total_years == 0 and len(merged) > 0:
                total_years = 1.0
            return float(min(total_years, 40))

    return None


def extract_education_level(text: str) -> Optional[str]:
    """
    Identify academic degree level from text.

    Args:
        text: Text from job description or resume education section.

    Returns:
        Standardized degree level ('PhD', 'Master', 'Bachelor', 'Associate'), or None.
    """
    if not text:
        return None

    lower = text.lower()

    if re.search(r"\b(?:ph\.?d|doctorate|doctoral)\b", lower):
        return "PhD"
    if re.search(r"\b(?:master(?:'s)?|m\.?tech|m\.?s\.?|mba|mca|m\.?e\.?)\b", lower):
        return "Master"
    if re.search(r"\b(?:bachelor(?:'s)?|b\.?tech|b\.?e\.?|b\.?s\.?|bca|b\.?sc)\b", lower):
        return "Bachelor"
    if re.search(r"\b(?:associate(?:'s)?|diploma)\b", lower):
        return "Associate"

    return None


def extract_job_requirements(job_description: str) -> Dict[str, Any]:
    """
    Extract structured requirements from a job description text.

    Separates required skills from preferred/nice-to-have skills, and
    identifies experience and education criteria without using an LLM.

    Args:
        job_description: Plain text or formatted job description.

    Returns:
        Dictionary containing:
        - required_skills: List of mandatory skill names
        - preferred_skills: List of preferred / bonus skill names
        - experience_requirement: Minimum years required (float) or None
        - education_requirement: Degree string ('Bachelor', 'Master', etc.) or None
    """
    cleaned_jd = clean_text(job_description)
    if not cleaned_jd:
        return {
            "required_skills": [],
            "preferred_skills": [],
            "experience_requirement": None,
            "education_requirement": None,
        }

    # Identify preferred vs required sections
    preferred_pattern = (
        r"(?:^|\n)\s*(?:preferred|nice\s*to\s*have|good\s*to\s*have|bonus|desired)"
        r"(?:\s*(?:qualifications|skills|requirements))?[:\-]?\s*(?:\n|$)"
    )
    pref_match = re.search(preferred_pattern, cleaned_jd, re.IGNORECASE)

    required_skills: List[str] = []
    preferred_skills: List[str] = []

    if pref_match:
        pref_start = pref_match.start()
        required_section = cleaned_jd[:pref_start]
        preferred_section = cleaned_jd[pref_start:]

        required_skills = extract_skills(required_section)
        preferred_skills = extract_skills(preferred_section)
        # Avoid putting required skills in preferred
        preferred_skills = [s for s in preferred_skills if s not in required_skills]
    else:
        # If no explicit preferred section, all extracted skills are primary requirements
        required_skills = extract_skills(cleaned_jd)
        preferred_skills = []

    exp_req = extract_years_of_experience(cleaned_jd)
    edu_req = extract_education_level(cleaned_jd)

    return {
        "required_skills": normalize_skill_list(required_skills),
        "preferred_skills": normalize_skill_list(preferred_skills),
        "experience_requirement": exp_req,
        "education_requirement": edu_req,
    }


def calculate_match_score(
    resume_data: Dict[str, Any],
    job_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compute transparent 0–100 compatibility score between resume and job description.

    Documented Weights:
    - Skill Match: 70%
    - Experience Match: 20%
    - Education Match: 10%

    If experience or education criteria are unavailable, weights dynamically
    rebalance so the score remains fair and strictly within 0–100.

    Args:
        resume_data: Parsed resume dictionary (from parse_resume).
        job_data: Extracted job requirements (from extract_job_requirements).

    Returns:
        Structured match evaluation dictionary.
    """
    # 1. Skill Matching
    resume_skills_raw = resume_data.get("skills", [])
    resume_skills = set(normalize_skill_list(resume_skills_raw))

    req_skills = normalize_skill_list(job_data.get("required_skills", []))
    pref_skills = normalize_skill_list(job_data.get("preferred_skills", []))

    if req_skills:
        req_set = set(req_skills)
        matched_skills = sorted(list(resume_skills.intersection(req_set)))
        missing_skills = sorted(list(req_set - resume_skills))
        base_skill_score = (len(matched_skills) / len(req_skills)) * 100.0

        # Preferred skills give modest bonus points up to 100 max
        if pref_skills:
            matched_pref = resume_skills.intersection(set(pref_skills))
            pref_bonus = (len(matched_pref) / len(pref_skills)) * 5.0
        else:
            pref_bonus = 0.0

        skill_score = round(min(100.0, base_skill_score + pref_bonus), 1)
    else:
        # Job description specified no recognizable skills from our database
        matched_skills = []
        missing_skills = []
        skill_score = 100.0 if len(resume_skills) > 0 else 50.0

    # 2. Experience Matching
    job_exp = job_data.get("experience_requirement")
    cand_exp = extract_candidate_experience_years(resume_data.get("experience", ""))

    exp_evaluable = True
    if job_exp is None or job_exp == 0:
        # Experience requirement was not specified in the JD
        experience_score = 100.0
    elif cand_exp is not None:
        if cand_exp >= job_exp:
            experience_score = 100.0
        else:
            experience_score = round((cand_exp / job_exp) * 100.0, 1)
    else:
        # Job requires experience, but candidate experience could not be reliably extracted
        exp_evaluable = False
        experience_score = 0.0

    # 3. Education Matching
    job_edu = job_data.get("education_requirement")
    cand_edu = extract_education_level(resume_data.get("education", ""))

    edu_evaluable = True
    if job_edu is None:
        # No degree requirement specified
        education_score = 100.0
    elif cand_edu is not None:
        job_rank = DEGREE_TIERS.get(job_edu, 3)
        cand_rank = DEGREE_TIERS.get(cand_edu, 1)
        if cand_rank >= job_rank:
            education_score = 100.0
        else:
            education_score = max(40.0, round((cand_rank / job_rank) * 100.0, 1))
    else:
        # Degree required but none detected on resume
        edu_evaluable = False
        education_score = 0.0

    # 4. Transparent Weighted Scoring & Dynamic Re-weighting
    if exp_evaluable and edu_evaluable:
        w_skill = WEIGHT_SKILLS        # 0.70
        w_exp = WEIGHT_EXPERIENCE      # 0.20
        w_edu = WEIGHT_EDUCATION       # 0.10
    elif not exp_evaluable and edu_evaluable:
        # Rebalance between skills and education
        w_skill = 0.85
        w_exp = 0.0
        w_edu = 0.15
    elif exp_evaluable and not edu_evaluable:
        # Rebalance between skills and experience
        w_skill = 0.80
        w_exp = 0.20
        w_edu = 0.0
    else:
        # Only skills evaluable
        w_skill = 1.00
        w_exp = 0.0
        w_edu = 0.0

    overall_score = round(
        (skill_score * w_skill)
        + (experience_score * w_exp)
        + (education_score * w_edu),
        1,
    )
    overall_score = max(0.0, min(100.0, overall_score))

    # 5. Recommendation Labels
    if overall_score >= 75.0:
        recommendation = "Strong Match"
    elif overall_score >= 50.0:
        recommendation = "Moderate Match"
    else:
        recommendation = "Needs Improvement"

    # 6. Detailed Explanation Narrative
    explanation_parts = []
    if req_skills:
        explanation_parts.append(
            f"Candidate matches {len(matched_skills)} of {len(req_skills)} required technical skills ({skill_score}% skill alignment)."
        )
        if missing_skills:
            explanation_parts.append(f"Key skill gaps: {', '.join(missing_skills)}.")
        else:
            explanation_parts.append("All primary required skills are present.")
    else:
        explanation_parts.append("No specific required skills identified in job description.")

    if job_exp is not None:
        if exp_evaluable:
            explanation_parts.append(
                f"Experience: Candidate demonstrates ~{cand_exp:g} year(s) vs {job_exp:g} year(s) required."
            )
        else:
            explanation_parts.append(
                f"Experience: Job requires {job_exp:g} year(s), but resume experience duration was not reliably parseable (scoring re-weighted to skills)."
            )
    else:
        explanation_parts.append("No strict years of experience requirement specified in job description.")

    if job_edu is not None:
        if edu_evaluable:
            explanation_parts.append(
                f"Education: Candidate holds {cand_edu} degree against requested {job_edu} requirement."
            )
        else:
            explanation_parts.append(
                f"Education: Job requests {job_edu} degree; candidate education was not explicitly identified."
            )

    explanation = " ".join(explanation_parts)

    return {
        "overall_score": overall_score,
        "skill_score": skill_score,
        "experience_score": experience_score if exp_evaluable else 0.0,
        "education_score": education_score if edu_evaluable else 0.0,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommendation": recommendation,
        "explanation": explanation,
    }
