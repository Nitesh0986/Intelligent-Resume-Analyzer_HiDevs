"""
Utility package for Intelligent Resume Analyzer.
Provides text preprocessing, skill extraction, PDF parsing, and job matching modules.
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
]
