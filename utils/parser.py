"""
Resume Parser Module for Intelligent Resume Analyzer.

Provides core PDF text extraction, entity extraction (Name, Email, Phone),
section segmentation (Experience, Education), and JSON export utilities.
"""

import io
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pypdf
from .preprocess import clean_text
from .skill_extractor import extract_skills

logger = logging.getLogger(__name__)

# Standard resume section headers used to delineate sections
COMMON_SECTION_HEADERS = [
    "experience",
    "work experience",
    "professional experience",
    "employment",
    "employment history",
    "career history",
    "work history",
    "education",
    "educational background",
    "academic background",
    "academic history",
    "qualifications",
    "skills",
    "technical skills",
    "core competencies",
    "technologies",
    "projects",
    "academic projects",
    "certifications",
    "certificates",
    "licenses",
    "awards",
    "achievements",
    "honors",
    "publications",
    "languages",
    "interests",
    "hobbies",
    "summary",
    "professional summary",
    "profile",
    "objective",
    "career objective",
    "declaration",
]


def extract_text_from_pdf(pdf_file: Union[str, Path, io.BytesIO, Any]) -> str:
    """
    Extract text content across all pages from a PDF file or file-like object.

    Handles empty pages, encrypted files, and corrupted streams gracefully.

    Args:
        pdf_file: File path (str or Path) or file-like object (e.g. BytesIO, UploadedFile).

    Returns:
        Cleaned, normalized text extracted from the PDF.

    Raises:
        ValueError: If the PDF cannot be opened, is encrypted, or is corrupted.
    """
    if pdf_file is None:
        raise ValueError("No PDF file was provided.")

    try:
        # pypdf can read from path or file-like object
        reader = pypdf.PdfReader(pdf_file)

        if reader.is_encrypted:
            # Attempt empty password decryption if possible
            try:
                reader.decrypt("")
            except Exception:
                raise ValueError("PDF is password-protected and cannot be read.")

        if len(reader.pages) == 0:
            logger.warning("PDF document contains 0 pages.")
            return ""

        extracted_pages: List[str] = []
        for idx, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text() or ""
                extracted_pages.append(page_text)
            except Exception as page_err:
                logger.warning("Failed to extract text from page %d: %s", idx + 1, page_err)

        raw_text = "\n".join(extracted_pages)
        return clean_text(raw_text)

    except pypdf.errors.PdfReadError as pe:
        logger.error("PyPDF Read Error: %s", pe)
        raise ValueError(f"Corrupted or unreadable PDF document: {pe}")
    except Exception as e:
        logger.error("Unexpected error during PDF extraction: %s", e)
        raise ValueError(f"Failed to process PDF file: {str(e)}")


def extract_email(text: str, as_dict: bool = False) -> Optional[Union[str, Dict[str, str]]]:
    """
    Extract the primary email address from the resume text using regex.

    Args:
        text: Normalized text from the resume.
        as_dict: If True, returns {'email': '...'} or None. If False, returns '...' or None.

    Returns:
        Email string, dictionary with 'email' key, or None if not found.
    """
    if not text:
        return None

    # Matches standard email patterns (RFC 5322 compatible subset)
    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    match = re.search(pattern, text)
    if not match:
        return None

    email = match.group(0).strip().rstrip(".").lower()
    if as_dict:
        return {"email": email}
    return email


def extract_phone(text: str) -> Optional[str]:
    """
    Extract a phone number from text supporting Indian (+91) and international formats.

    Args:
        text: Normalized text from the resume.

    Returns:
        Standardized phone number string, or None if not found.
    """
    if not text:
        return None

    # Pattern covers:
    # - +91 9876543210 / +91-98765-43210 / 09876543210
    # - (123) 456-7890 / 123-456-7890
    # - International format +1 234 567 8900
    phone_patterns = [
        # Indian format with country code: +91 98765 43210 or +91-9876543210
        r"(?:\+91[\-\s]?)?[6-9]\d{9}",
        # International with leading +: +1-555-555-5555 or +44 20 7123 4567
        r"\+\d{1,3}[\s\-]?(?:\(?\d{2,4}\)?[\s\-]?)?\d{3,4}[\s\-]?\d{3,4}",
        # US/General format: (123) 456-7890 or 123-456-7890
        r"(?:\(?\d{3}\)?[\s\-\.])\d{3}[\s\-\.]\d{4}",
    ]

    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            phone_str = match.group(0).strip()
            # Verify phone string has at least 10 digits
            digits_only = re.sub(r"\D", "", phone_str)
            if 10 <= len(digits_only) <= 15:
                return phone_str

    return None


def extract_name(text: str) -> Optional[str]:
    """
    Extract candidate name using top-section line heuristics.

    Evaluates the first several non-empty lines, filtering out contact details,
    dates, URLs, and section titles.

    Args:
        text: Normalized text from the resume.

    Returns:
        Candidate name string, or None if no confident match is found.
    """
    if not text:
        return None

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Skip markers that cannot be names
    disallowed_keywords = {
        "resume", "curriculum", "vitae", "cv", "profile", "summary",
        "contact", "details", "phone", "email", "address", "page",
        "portfolio", "github", "linkedin", "experience", "education",
        "skills", "projects", "objective"
    }

    # Inspect the first 8 meaningful lines
    for line in lines[:8]:
        # Filter out lines containing email, URL, or phone patterns
        if "@" in line or "http" in line or "www." in line or ".com" in line:
            continue
        if re.search(r"\d{4,}", line):  # Lines with long numbers/dates/phones
            continue

        clean_line = re.sub(r"[^\w\s\.\-]", "", line).strip()
        words = clean_line.split()

        # Names typically consist of 2 to 4 words
        if 2 <= len(words) <= 4:
            # Check length reasonable for a name
            if 3 <= len(clean_line) <= 45:
                # Ensure no disallowed keyword is in the line
                lower_words = [w.lower() for w in words]
                if any(w in disallowed_keywords for w in lower_words):
                    continue

                # Ensure words are mostly alphabetic
                if all(re.match(r"^[A-Za-z\.\-]+$", w) for w in words):
                    # Check capitalization: either ALL UPPER or Title Case
                    if clean_line.isupper() or all(w[0].isupper() for w in words if w):
                        return clean_line.title()

    # Fallback: check first non-empty line if single or two words
    if lines:
        first_line = lines[0].strip()
        first_words = first_line.split()
        if 1 <= len(first_words) <= 3 and len(first_line) <= 35:
            if not any(k in first_line.lower() for k in disallowed_keywords) and "@" not in first_line:
                if all(re.match(r"^[A-Za-z\.\-]+$", w) for w in first_words):
                    return first_line.title()

    return None


def _extract_section_text(text: str, target_headers: List[str]) -> str:
    """
    Helper to locate a section by its header and extract lines until the next header.
    """
    if not text:
        return ""

    # Build regex pattern for headers that appear as distinct lines or headings
    header_pattern = r"(?:^|\n)\s*(" + "|".join(re.escape(h) for h in target_headers) + r")\s*[:\-]?\s*(?:\n|$)"
    match = re.search(header_pattern, text, re.IGNORECASE)

    if not match:
        return ""

    start_pos = match.end()
    remaining_text = text[start_pos:]

    # Build pattern for all other known headers to find the section boundary
    all_other_headers = [h for h in COMMON_SECTION_HEADERS if h.lower() not in [t.lower() for t in target_headers]]
    stop_pattern = r"(?:^|\n)\s*(" + "|".join(re.escape(h) for h in all_other_headers) + r")\s*[:\-]?\s*(?:\n|$)"

    stop_match = re.search(stop_pattern, remaining_text, re.IGNORECASE)
    if stop_match:
        section_content = remaining_text[: stop_match.start()]
    else:
        section_content = remaining_text

    return section_content.strip()


def extract_experience(text: str) -> str:
    """
    Extract the work experience / professional background section.

    Args:
        text: Normalized text from the resume.

    Returns:
        Extracted experience section text, or empty string if not detected.
    """
    target_headers = [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "career history",
        "work history",
        "professional background",
    ]
    return _extract_section_text(text, target_headers)


def extract_education(text: str) -> str:
    """
    Extract the education / academic qualifications section.

    Args:
        text: Normalized text from the resume.

    Returns:
        Extracted education section text, or empty string if not detected.
    """
    target_headers = [
        "education",
        "educational background",
        "academic background",
        "academic history",
        "qualifications",
        "academic qualifications",
        "education and training",
    ]
    return _extract_section_text(text, target_headers)


def parse_resume(source: Union[str, Path, io.BytesIO, Any]) -> Dict[str, Any]:
    """
    Parse a resume from a PDF file, file-like object, or raw text string.

    Orchestrates:
    1. Text extraction (if PDF)
    2. Text sanitization
    3. Entity extraction (Name, Email, Phone)
    4. Skill identification
    5. Section segmentation (Education, Experience)

    Args:
        source: PDF path, file-like object, or pre-extracted text string.

    Returns:
        Dictionary adhering to the Day 1 structured schema.
    """
    # Determine whether input is raw text or a PDF source
    if isinstance(source, str) and not source.lower().endswith(".pdf") and len(source) > 200:
        # Pre-extracted text passed directly
        cleaned_text = clean_text(source)
    else:
        cleaned_text = extract_text_from_pdf(source)

    name = extract_name(cleaned_text)
    email = extract_email(cleaned_text, as_dict=False)
    phone = extract_phone(cleaned_text)
    skills = extract_skills(cleaned_text)
    education = extract_education(cleaned_text)
    experience = extract_experience(cleaned_text)

    return {
        "name": name or "",
        "email": email or "",
        "phone": phone or "",
        "skills": skills,
        "education": education or "",
        "experience": experience or "",
    }


def save_parsed_resume(
    data: Dict[str, Any],
    output_dir: Union[str, Path] = "outputs/parsed_resumes",
    filename: Optional[str] = None,
) -> Path:
    """
    Save parsed resume dictionary to a formatted JSON file.

    Args:
        data: Structured resume dictionary.
        output_dir: Directory path for storage.
        filename: Optional custom filename. If None, uses parsed_resume_YYYYMMDD_HHMMSS.json.

    Returns:
        Path to the saved JSON file.
    """
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"parsed_resume_{timestamp}.json"

    file_path = target_dir / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    logger.info("Saved parsed resume to: %s", file_path)
    return file_path
