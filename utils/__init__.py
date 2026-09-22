"""
Utility package for Intelligent Resume Analyzer.
Provides text preprocessing, skill extraction, PDF parsing, job matching,
and professional report generation modules.
"""

from .preprocess import clean_text
from .skill_extractor import (
    extract_skills,
    normalize_skill,
    normalize_skill_list,
    SKILLS_DATABASE,
)
from .parser import (
    extract_text_from_pdf,
    extract_email,
    extract_phone,
    extract_name,
    extract_experience,
    extract_education,
    parse_resume,
    save_parsed_resume,
)
from .matcher import (
    extract_job_requirements,
    extract_years_of_experience,
    extract_candidate_experience_years,
    extract_education_level,
    calculate_match_score,
    WEIGHT_SKILLS,
    WEIGHT_EXPERIENCE,
    WEIGHT_EDUCATION,
)
from .reporter import (
    generate_candidate_summary,
    identify_strengths,
    identify_skill_gaps,
    analyze_experience_alignment,
    analyze_education_alignment,
    generate_candidate_analysis,
    generate_human_readable_report,
    save_candidate_report,
)

__all__ = [
    "clean_text",
    "extract_skills",
    "normalize_skill",
    "normalize_skill_list",
    "SKILLS_DATABASE",
    "extract_text_from_pdf",
    "extract_email",
    "extract_phone",
    "extract_name",
    "extract_experience",
    "extract_education",
    "parse_resume",
    "save_parsed_resume",
    "extract_job_requirements",
    "extract_years_of_experience",
    "extract_candidate_experience_years",
    "extract_education_level",
    "calculate_match_score",
    "WEIGHT_SKILLS",
    "WEIGHT_EXPERIENCE",
    "WEIGHT_EDUCATION",
    "generate_candidate_summary",
    "identify_strengths",
    "identify_skill_gaps",
    "analyze_experience_alignment",
    "analyze_education_alignment",
    "generate_candidate_analysis",
    "generate_human_readable_report",
    "save_candidate_report",
]
