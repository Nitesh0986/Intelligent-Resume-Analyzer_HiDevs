"""
Candidate Analysis and Report Generation Module for Intelligent Resume Analyzer.

Provides deterministic, factual candidate summarization, strength identification,
skill gap assessment, experience/education alignment narratives, and report export utilities.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .matcher import (
    DEGREE_TIERS,
    extract_candidate_experience_years,
    extract_education_level,
)
from .skill_extractor import normalize_skill_list

logger = logging.getLogger(__name__)


def generate_candidate_summary(resume_data: Dict[str, Any]) -> str:
    """
    Generate a concise factual summary based ONLY on extracted resume information.

    Does not invent companies, experience duration, skills, or degrees.

    Args:
        resume_data: Parsed resume dictionary.

    Returns:
        Factual summary string.
    """
    if not isinstance(resume_data, dict) or not resume_data:
        return "No candidate information available to summarize."

    name = resume_data.get("name") if isinstance(resume_data.get("name"), str) and resume_data.get("name") else "The candidate"
    raw_skills = resume_data.get("skills")
    skills = [s for s in raw_skills if isinstance(s, str)] if isinstance(raw_skills, list) else []
    exp_text = resume_data.get("experience") if isinstance(resume_data.get("experience"), str) else ""
    edu_text = resume_data.get("education") if isinstance(resume_data.get("education"), str) else ""

    summary_parts = []

    # 1. Identity & Skills
    if skills:
        top_skills = ", ".join(skills[:8])
        more = f" and {len(skills) - 8} more" if len(skills) > 8 else ""
        summary_parts.append(
            f"{name} demonstrates verified technical competencies in {top_skills}{more}."
        )
    else:
        summary_parts.append(f"{name} has an active profile with no distinct technical skills extracted.")

    # 2. Experience verification
    cand_years = extract_candidate_experience_years(exp_text)
    if cand_years is not None and cand_years > 0:
        summary_parts.append(
            f"The professional background reflects approximately {cand_years:g} year(s) of documented experience."
        )
    elif exp_text.strip():
        summary_parts.append(
            "Documented professional background is present in the resume."
        )
    else:
        summary_parts.append("No distinct work experience history was identified in the document.")

    # 3. Education verification
    cand_degree = extract_education_level(edu_text)
    if cand_degree:
        summary_parts.append(f"Holds an academic qualification at the {cand_degree} level.")
    elif edu_text.strip():
        summary_parts.append("Academic qualifications are referenced in the educational background.")
    else:
        summary_parts.append("No specific degree level was explicitly identified.")

    return " ".join(summary_parts)


def identify_strengths(
    resume_data: Dict[str, Any],
    job_data: Dict[str, Any],
    match_result: Dict[str, Any],
) -> List[str]:
    """
    Deterministically identify verified candidate strengths aligned with the job.

    Args:
        resume_data: Parsed resume dictionary.
        job_data: Extracted job requirements.
        match_result: Computed match evaluation.

    Returns:
        List of factual strength statements.
    """
    resume_data = resume_data if isinstance(resume_data, dict) else {}
    job_data = job_data if isinstance(job_data, dict) else {}
    match_result = match_result if isinstance(match_result, dict) else {}

    strengths: List[str] = []

    raw_matched = match_result.get("matched_skills")
    matched_skills = raw_matched if isinstance(raw_matched, list) else []
    if matched_skills:
        strengths.append(
            f"Demonstrated proficiency in key required skills: {', '.join(str(s) for s in matched_skills)}."
        )

    # Preferred / Bonus skills
    raw_res_skills = resume_data.get("skills")
    resume_skills = set(normalize_skill_list(raw_res_skills)) if isinstance(raw_res_skills, list) else set()

    raw_pref_skills = job_data.get("preferred_skills")
    pref_skills = set(normalize_skill_list(raw_pref_skills)) if isinstance(raw_pref_skills, list) else set()

    matched_pref = sorted(list(resume_skills.intersection(pref_skills)))
    if matched_pref:
        strengths.append(
            f"Offers desirable preferred qualifications: {', '.join(matched_pref)}."
        )

    # Experience alignment
    job_exp = job_data.get("experience_requirement")
    exp_text = resume_data.get("experience") if isinstance(resume_data.get("experience"), str) else ""
    cand_exp = extract_candidate_experience_years(exp_text)

    if isinstance(job_exp, (int, float)) and cand_exp is not None:
        if cand_exp >= job_exp:
            strengths.append(
                f"Meets or exceeds the required tenure (~{cand_exp:g} years documented vs {job_exp:g} years required)."
            )

    # Education alignment
    job_edu = job_data.get("education_requirement") if isinstance(job_data.get("education_requirement"), str) else None
    edu_text = resume_data.get("education") if isinstance(resume_data.get("education"), str) else ""
    cand_edu = extract_education_level(edu_text)

    if job_edu and cand_edu:
        job_rank = DEGREE_TIERS.get(job_edu, 3)
        cand_rank = DEGREE_TIERS.get(cand_edu, 1)
        if cand_rank >= job_rank:
            strengths.append(
                f"Meets academic credential standards with a verified {cand_edu} degree."
            )

    # High overall score
    raw_score = match_result.get("overall_score")
    try:
        score = float(raw_score)
    except (ValueError, TypeError):
        score = 0.0

    if score >= 75.0:
        strengths.append(
            f"High overall compatibility score of {score:.1f}/100 indicating strong role alignment."
        )

    if not strengths:
        strengths.append("Candidate demonstrates baseline domain exposure relevant to technical roles.")

    return strengths


def identify_skill_gaps(
    job_data: Dict[str, Any],
    match_result: Dict[str, Any],
) -> List[str]:
    """
    Itemize missing required skills without fabricating unmentioned criteria.

    Args:
        job_data: Extracted job requirements.
        match_result: Computed match evaluation.

    Returns:
        List of descriptive skill gap statements.
    """
    match_result = match_result if isinstance(match_result, dict) else {}
    raw_missing = match_result.get("missing_skills")
    missing_skills = raw_missing if isinstance(raw_missing, list) else []

    if not missing_skills:
        return ["All primary required skills are satisfied with no detected gaps."]

    gaps = []
    for skill in missing_skills:
        gaps.append(f"Required Skill: {skill} -> Status: Missing from candidate resume.")

    return gaps


def analyze_experience_alignment(
    resume_data: Dict[str, Any],
    job_data: Dict[str, Any],
    match_result: Dict[str, Any],
) -> str:
    """
    Explain whether the available resume experience aligns with the job requirement.

    Args:
        resume_data: Parsed resume dictionary.
        job_data: Extracted job requirements.
        match_result: Computed match evaluation.

    Returns:
        Detailed experience analysis narrative.
    """
    resume_data = resume_data if isinstance(resume_data, dict) else {}
    job_data = job_data if isinstance(job_data, dict) else {}

    raw_job_exp = job_data.get("experience_requirement")
    job_exp = raw_job_exp if isinstance(raw_job_exp, (int, float)) else None

    exp_text = resume_data.get("experience") if isinstance(resume_data.get("experience"), str) else ""
    cand_exp = extract_candidate_experience_years(exp_text)

    if job_exp is not None:
        if cand_exp is not None:
            if cand_exp >= job_exp:
                return (
                    f"Candidate demonstrates approximately {cand_exp:g} year(s) of documented experience, "
                    f"satisfying the target requirement of {job_exp:g}+ year(s)."
                )
            else:
                deficit = job_exp - cand_exp
                return (
                    f"Candidate demonstrates approximately {cand_exp:g} year(s) of documented experience, "
                    f"which is below the stated requirement of {job_exp:g} year(s) (tenure gap of ~{deficit:g} year(s))."
                )
        else:
            return (
                f"The job requires {job_exp:g} year(s) of experience, but candidate experience duration "
                "could not be reliably quantified from the provided resume text."
            )
    else:
        if cand_exp is not None:
            return (
                f"Candidate exhibits approximately {cand_exp:g} year(s) of documented experience. "
                "No mandatory minimum tenure was specified in the job description."
            )
        else:
            return "No specific years of experience requirement was specified in the job description."


def analyze_education_alignment(
    resume_data: Dict[str, Any],
    job_data: Dict[str, Any],
    match_result: Dict[str, Any],
) -> str:
    """
    Compare available education information against the job requirement.

    Args:
        resume_data: Parsed resume dictionary.
        job_data: Extracted job requirements.
        match_result: Computed match evaluation.

    Returns:
        Detailed education analysis narrative.
    """
    resume_data = resume_data if isinstance(resume_data, dict) else {}
    job_data = job_data if isinstance(job_data, dict) else {}

    raw_job_edu = job_data.get("education_requirement")
    job_edu = raw_job_edu if isinstance(raw_job_edu, str) else None

    edu_text = resume_data.get("education") if isinstance(resume_data.get("education"), str) else ""
    cand_edu = extract_education_level(edu_text)

    if job_edu is not None:
        if cand_edu is not None:
            job_rank = DEGREE_TIERS.get(job_edu, 3)
            cand_rank = DEGREE_TIERS.get(cand_edu, 1)
            if cand_rank >= job_rank:
                return (
                    f"Candidate holds a {cand_edu} degree, which fulfills or exceeds the requested "
                    f"{job_edu} degree prerequisite."
                )
            else:
                return (
                    f"Candidate holds a {cand_edu} degree, which is below the requested "
                    f"{job_edu} prerequisite."
                )
        else:
            return (
                f"The job description requests a {job_edu} degree; candidate resume does not "
                "explicitly mention a recognized academic degree level."
            )
    else:
        if cand_edu is not None:
            return (
                f"Candidate holds a {cand_edu} degree. No formal minimum degree was required "
                "in the job description."
            )
        else:
            return "No formal academic degree requirement was specified in the job description."


def generate_candidate_analysis(
    resume_data: Dict[str, Any],
    job_data: Dict[str, Any],
    match_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate professional candidate analysis adhering to the Day 3 specification.

    Args:
        resume_data: Parsed resume dictionary.
        job_data: Extracted job requirements.
        match_result: Computed match evaluation dictionary.

    Returns:
        Structured candidate analysis dictionary.
    """
    resume_data = resume_data if isinstance(resume_data, dict) else {}
    job_data = job_data if isinstance(job_data, dict) else {}
    match_result = match_result if isinstance(match_result, dict) else {}

    summary = generate_candidate_summary(resume_data)
    strengths = identify_strengths(resume_data, job_data, match_result)
    skill_gaps = identify_skill_gaps(job_data, match_result)
    exp_analysis = analyze_experience_alignment(resume_data, job_data, match_result)
    edu_analysis = analyze_education_alignment(resume_data, job_data, match_result)

    raw_score = match_result.get("overall_score", 0.0)
    try:
        score = float(raw_score)
    except (ValueError, TypeError):
        score = 0.0

    raw_rec = match_result.get("recommendation")
    rec = str(raw_rec) if raw_rec else "Needs Improvement"

    raw_matched = match_result.get("matched_skills")
    matched_skills = raw_matched if isinstance(raw_matched, list) else []

    raw_missing = match_result.get("missing_skills")
    missing_skills = raw_missing if isinstance(raw_missing, list) else []

    return {
        "candidate_summary": summary,
        "overall_score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "strengths": strengths,
        "skill_gaps": skill_gaps,
        "experience_analysis": exp_analysis,
        "education_analysis": edu_analysis,
        "recommendation": rec,
        "generated_at": datetime.now().isoformat(),
    }


def generate_human_readable_report(
    analysis: Dict[str, Any],
    candidate_info: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Format candidate analysis into a clean, human-readable text document.

    Args:
        analysis: Dictionary produced by generate_candidate_analysis.
        candidate_info: Optional dict with candidate name and email.

    Returns:
        Formatted report string.
    """
    cand = candidate_info if isinstance(candidate_info, dict) else {}
    name = cand.get("name") or "Not Specified"
    email = cand.get("email") or "Not Specified"

    raw_score = analysis.get("overall_score", 0.0)
    try:
        score = float(raw_score)
    except (ValueError, TypeError):
        score = 0.0

    rec = analysis.get("recommendation", "Not Evaluated")
    timestamp = analysis.get("generated_at", datetime.now().isoformat())

    raw_matched = analysis.get("matched_skills")
    matched = raw_matched if isinstance(raw_matched, list) else []

    raw_missing = analysis.get("missing_skills")
    missing = raw_missing if isinstance(raw_missing, list) else []

    raw_strengths = analysis.get("strengths")
    strengths = raw_strengths if isinstance(raw_strengths, list) else []

    raw_gaps = analysis.get("skill_gaps")
    gaps = raw_gaps if isinstance(raw_gaps, list) else []

    matched_lines = "\n".join(f"- {s}" for s in matched) if matched else "- None"
    missing_lines = "\n".join(f"- {s}" for s in missing) if missing else "- None (All required skills present)"
    strength_lines = "\n".join(f"- {s}" for s in strengths) if strengths else "- None documented"
    gap_lines = "\n".join(f"- {g}" for g in gaps) if gaps else "- None"

    report = f"""==================================================
INTELLIGENT RESUME ANALYZER — CANDIDATE REPORT
==================================================

Candidate: {name}
Email:     {email}
Generated: {timestamp}

--------------------------------------------------
OVERALL COMPATIBILITY SCORE: {score:.1f} / 100
RECOMMENDATION: {rec}
--------------------------------------------------

CANDIDATE SUMMARY
-----------------
{analysis.get('candidate_summary', 'N/A')}

MATCHED SKILLS
--------------
{matched_lines}

MISSING SKILLS
--------------
{missing_lines}

STRENGTHS
---------
{strength_lines}

SKILL GAPS
----------
{gap_lines}

EXPERIENCE ANALYSIS
-------------------
{analysis.get('experience_analysis', 'N/A')}

EDUCATION ANALYSIS
------------------
{analysis.get('education_analysis', 'N/A')}

RECOMMENDATION
--------------
{rec}

==================================================
DISCLAIMER: This automated report is an algorithmic
compatibility assessment based on observable criteria.
It does not constitute an actual hiring decision.
==================================================
"""
    return report.strip()


def save_candidate_report(
    analysis: Dict[str, Any],
    output_dir: Union[str, Path] = "outputs/reports",
    filename: Optional[str] = None,
) -> Path:
    """
    Save candidate analysis report as formatted JSON.

    Args:
        analysis: Analysis dictionary.
        output_dir: Target directory.
        filename: Optional filename. If omitted, uses candidate_report_YYYYMMDD_HHMMSS.json.

    Returns:
        Path to the saved file.
    """
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"candidate_report_{timestamp}.json"

    file_path = target_dir / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=4, ensure_ascii=False)

    logger.info("Saved candidate report to: %s", file_path)
    return file_path
