"""
Unit and integration tests for Intelligent Resume Analyzer.
Verifies parsing, preprocessing, skill extraction, regex extractors, and JSON export.
"""

import io
import json
import pytest
import pypdf

from utils.preprocess import clean_text
from utils.skill_extractor import extract_skills
from utils.parser import (
    extract_text_from_pdf,
    extract_email,
    extract_phone,
    extract_name,
    extract_experience,
    extract_education,
    parse_resume,
    save_parsed_resume,
)


# Sample synthetic text for testing
SAMPLE_RESUME_TEXT = """
JOHN DOE
Software Engineer
Email: john.doe@gmail.com | Phone: +91 9876543210
Location: Bangalore, India

PROFESSIONAL SUMMARY
Experienced Software Engineer specializing in Python, FastAPI, and Cloud solutions.

TECHNICAL SKILLS
- Programming Languages: Python, C++, Java, JavaScript, TypeScript
- Frameworks: React, Node.js, Express, FastAPI, Flask, Streamlit
- Databases: PostgreSQL, MongoDB, MySQL, Redis
- Cloud & DevOps: Docker, Kubernetes, AWS, Git, GitHub
- AI & Data Science: Machine Learning, Scikit-learn, Pandas, NumPy

WORK EXPERIENCE
Senior Software Engineer - TechCorp Inc. (2022 - Present)
- Architected RESTful microservices using Python and FastAPI.
- Implemented real-time data streaming using Redis and PostgreSQL.
- Containerized applications using Docker and orchestrated deployments on AWS.

Junior Developer - CodeBase Ltd. (2020 - 2022)
- Built dynamic UI dashboards using React and TypeScript.
- Developed backend endpoints with Node.js and Express.

EDUCATION
Master of Science in Computer Science
National Institute of Technology (2018 - 2020)
GPA: 3.9/4.0

Bachelor of Technology in Information Technology
ABC University (2014 - 2018)
First Class with Distinction

PROJECTS
Intelligent Resume Analyzer: Built automated resume parser with Streamlit.
"""


def test_clean_text_normalizes_spacing_and_bullets():
    raw = "  Line 1   with   spaces\r\n\r\n\r\n\r\n• Bullet item \u00a0with nonbreaking space\n\n\n- Another item  "
    cleaned = clean_text(raw)
    assert "Line 1 with spaces" in cleaned
    assert "- Bullet item with nonbreaking space" in cleaned
    assert "\n\n\n" not in cleaned  # Max 2 consecutive newlines
    assert clean_text(None) == ""
    assert clean_text("") == ""


def test_extract_email():
    text = "Please reach out to me at alice.smith_dev@example.org or visit my site."
    assert extract_email(text) == "alice.smith_dev@example.org"
    assert extract_email(text, as_dict=True) == {"email": "alice.smith_dev@example.org"}
    assert extract_email("No email here 12345") is None
    assert extract_email(None) is None


def test_extract_phone():
    # Indian formats
    assert extract_phone("Contact: +91 9876543210") == "+91 9876543210"
    assert extract_phone("Mob: +91-9123456789") == "+91-9123456789"
    assert extract_phone("Direct: 9876543210") == "9876543210"
    
    # International formats
    assert extract_phone("Call: +1-555-234-5678") == "+1-555-234-5678"
    assert extract_phone("US: (123) 456-7890") == "(123) 456-7890"

    # Missing phone
    assert extract_phone("No phone number present here.") is None
    assert extract_phone(None) is None


def test_extract_name():
    assert extract_name(SAMPLE_RESUME_TEXT) == "John Doe"

    # Name in title case with initials
    custom_resume = "Dr. Jane K. Doe\nData Scientist\njane@data.io"
    assert extract_name(custom_resume) == "Dr. Jane K. Doe"

    # Should ignore generic resume headers
    resume_with_header = "CURRICULUM VITAE\n\nRobert Downey\nSoftware Architect"
    assert extract_name(resume_with_header) == "Robert Downey"


def test_extract_skills():
    text = "Proficient in Python, C++, Docker, React, AWS, FastAPI, and machine learning."
    skills = extract_skills(text)

    assert "Python" in skills
    assert "C++" in skills
    assert "Docker" in skills
    assert "React" in skills
    assert "AWS" in skills
    assert "FastAPI" in skills
    assert "Machine Learning" in skills

    # Ensure no duplicates and case-insensitivity
    assert extract_skills("python, PYTHON, PyThOn") == ["Python"]

    # Boundary safety: "Java" should NOT match "JavaScript"
    js_only = "Experienced with JavaScript and TypeScript."
    assert "JavaScript" in extract_skills(js_only)
    assert "Java" not in extract_skills(js_only)

    # Empty text
    assert extract_skills("") == []


def test_extract_experience():
    exp = extract_experience(SAMPLE_RESUME_TEXT)
    assert "Senior Software Engineer - TechCorp Inc." in exp
    assert "Junior Developer - CodeBase Ltd." in exp
    assert "Master of Science in Computer Science" not in exp  # Education boundary respected


def test_extract_education():
    edu = extract_education(SAMPLE_RESUME_TEXT)
    assert "Master of Science in Computer Science" in edu
    assert "ABC University" in edu
    assert "Senior Software Engineer" not in edu  # Experience boundary respected


def test_parse_resume_structured():
    result = parse_resume(SAMPLE_RESUME_TEXT)
    assert result["name"] == "John Doe"
    assert result["email"] == "john.doe@gmail.com"
    assert result["phone"] == "+91 9876543210"
    assert "Python" in result["skills"]
    assert "FastAPI" in result["skills"]
    assert len(result["skills"]) > 5
    assert "TechCorp" in result["experience"]
    assert "Computer Science" in result["education"]


def test_save_parsed_resume(tmp_path):
    data = {
        "name": "Test Candidate",
        "email": "candidate@test.com",
        "phone": "+91 9999999999",
        "skills": ["Python", "SQL"],
        "education": "BS in CS",
        "experience": "5 years dev",
    }
    saved_path = save_parsed_resume(data, output_dir=tmp_path)
    assert saved_path.exists()
    assert saved_path.suffix == ".json"

    with open(saved_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded == data


def test_pdf_extraction_with_synthetic_pdf():
    # Create an in-memory PDF using pypdf PdfWriter
    writer = pypdf.PdfWriter()
    # Adding a blank page
    writer.add_blank_page(width=612, height=792)
    pdf_bytes = io.BytesIO()
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)

    # Empty page extraction should return empty string cleanly without crashing
    text = extract_text_from_pdf(pdf_bytes)
    assert text == ""


def test_invalid_pdf_handling():
    # Corrupted / non-pdf bytes
    corrupted_data = io.BytesIO(b"This is not a valid PDF header")
    with pytest.raises(ValueError, match="Corrupted or unreadable PDF"):
        extract_text_from_pdf(corrupted_data)

    # None file
    with pytest.raises(ValueError, match="No PDF file was provided"):
        extract_text_from_pdf(None)
