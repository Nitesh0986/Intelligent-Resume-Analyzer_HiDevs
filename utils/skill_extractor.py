"""
Skill Extraction Module for Intelligent Resume Analyzer.

Provides a structured, extensible dictionary of software, engineering, and
data science skills, and a case-insensitive extractor with symbol-safe boundary detection.
"""

import re
from typing import List, Dict, Set


# Extensible database mapping canonical skill names to regex patterns.
# Note: Patterns use lookaround assertions for clean boundary matching.
SKILLS_DATABASE: Dict[str, List[str]] = {
    # Programming Languages
    "Python": [r"(?<![a-zA-Z0-9])python(?:3)?(?![a-zA-Z0-9])"],
    "C": [r"(?<![a-zA-Z0-9])c(?![a-zA-Z0-9+#])"],  # Isolated C, avoiding C++ or C#
    "C++": [r"(?<![a-zA-Z0-9])c\+\+(?![a-zA-Z0-9+])"],
    "C#": [r"(?<![a-zA-Z0-9])(?:c\#|c-sharp)(?![a-zA-Z0-9#])"],
    "Java": [r"(?<![a-zA-Z0-9])java(?![a-zA-Z0-9]|\s*script)"],  # Match Java, not JavaScript
    "JavaScript": [r"(?<![a-zA-Z0-9])(?:javascript|js)(?![a-zA-Z0-9])"],
    "TypeScript": [r"(?<![a-zA-Z0-9])(?:typescript|ts)(?![a-zA-Z0-9])"],
    "Go": [r"(?<![a-zA-Z0-9])(?:golang|go)(?![a-zA-Z0-9])"],
    "Rust": [r"(?<![a-zA-Z0-9])rust(?![a-zA-Z0-9])"],
    "PHP": [r"(?<![a-zA-Z0-9])php(?![a-zA-Z0-9])"],
    "Ruby": [r"(?<![a-zA-Z0-9])ruby(?![a-zA-Z0-9])"],
    "R": [r"(?<![a-zA-Z0-9])r(?![a-zA-Z0-9+#])"],
    "Swift": [r"(?<![a-zA-Z0-9])swift(?![a-zA-Z0-9])"],
    "Kotlin": [r"(?<![a-zA-Z0-9])kotlin(?![a-zA-Z0-9])"],

    # Web & Full Stack Frameworks
    "React": [r"(?<![a-zA-Z0-9])(?:react(?:\.?js)?|react-native)(?![a-zA-Z0-9])"],
    "Node.js": [r"(?<![a-zA-Z0-9])(?:node(?:\.?js)?)(?![a-zA-Z0-9])"],
    "Express": [r"(?<![a-zA-Z0-9])(?:express(?:\.?js)?)(?![a-zA-Z0-9])"],
    "HTML": [r"(?<![a-zA-Z0-9])(?:html|html5)(?![a-zA-Z0-9])"],
    "CSS": [r"(?<![a-zA-Z0-9])(?:css|css3)(?![a-zA-Z0-9])"],
    "FastAPI": [r"(?<![a-zA-Z0-9])fastapi(?![a-zA-Z0-9])"],
    "Flask": [r"(?<![a-zA-Z0-9])flask(?![a-zA-Z0-9])"],
    "Django": [r"(?<![a-zA-Z0-9])django(?![a-zA-Z0-9])"],
    "Next.js": [r"(?<![a-zA-Z0-9])next(?:\.?js)?(?![a-zA-Z0-9])"],
    "Vue.js": [r"(?<![a-zA-Z0-9])vue(?:\.?js)?(?![a-zA-Z0-9])"],
    "Angular": [r"(?<![a-zA-Z0-9])(?:angular|angularjs)(?![a-zA-Z0-9])"],
    "Tailwind CSS": [r"(?<![a-zA-Z0-9])tailwind(?:\s*css)?(?![a-zA-Z0-9])"],
    "Bootstrap": [r"(?<![a-zA-Z0-9])bootstrap(?![a-zA-Z0-9])"],
    "REST API": [r"(?<![a-zA-Z0-9])(?:restful\s*apis?|rest\s*apis?)(?![a-zA-Z0-9])"],
    "GraphQL": [r"(?<![a-zA-Z0-9])graphql(?![a-zA-Z0-9])"],

    # Databases & Caching
    "SQL": [r"(?<![a-zA-Z0-9])sql(?![a-zA-Z0-9])"],
    "MySQL": [r"(?<![a-zA-Z0-9])mysql(?![a-zA-Z0-9])"],
    "PostgreSQL": [r"(?<![a-zA-Z0-9])(?:postgresql|postgres)(?![a-zA-Z0-9])"],
    "MongoDB": [r"(?<![a-zA-Z0-9])(?:mongodb|mongo)(?![a-zA-Z0-9])"],
    "SQLite": [r"(?<![a-zA-Z0-9])sqlite(?![a-zA-Z0-9])"],
    "Redis": [r"(?<![a-zA-Z0-9])redis(?![a-zA-Z0-9])"],
    "Oracle": [r"(?<![a-zA-Z0-9])oracle\s*(?:db|database)?(?![a-zA-Z0-9])"],

    # DevOps, Cloud & Tools
    "Git": [r"(?<![a-zA-Z0-9])git(?![a-zA-Z0-9]|\s*(?:hub|lab))"],
    "GitHub": [r"(?<![a-zA-Z0-9])github(?![a-zA-Z0-9])"],
    "GitLab": [r"(?<![a-zA-Z0-9])gitlab(?![a-zA-Z0-9])"],
    "Docker": [r"(?<![a-zA-Z0-9])docker(?![a-zA-Z0-9])"],
    "Kubernetes": [r"(?<![a-zA-Z0-9])(?:kubernetes|k8s)(?![a-zA-Z0-9])"],
    "AWS": [r"(?<![a-zA-Z0-9])(?:aws|amazon\s*web\s*services)(?![a-zA-Z0-9])"],
    "Azure": [r"(?<![a-zA-Z0-9])(?:azure|microsoft\s*azure)(?![a-zA-Z0-9])"],
    "Google Cloud": [r"(?<![a-zA-Z0-9])(?:gcp|google\s*cloud)(?![a-zA-Z0-9])"],
    "Linux": [r"(?<![a-zA-Z0-9])(?:linux|ubuntu)(?![a-zA-Z0-9])"],
    "CI/CD": [r"(?<![a-zA-Z0-9])(?:ci[\s/-]?cd|continuous\s*integration)(?![a-zA-Z0-9])"],
    "Bash": [r"(?<![a-zA-Z0-9])(?:bash|shell\s*scripting?)(?![a-zA-Z0-9])"],

    # Data Science, AI & Machine Learning
    "Machine Learning": [r"(?<![a-zA-Z0-9])(?:machine\s*learning|\bml\b)(?![a-zA-Z0-9])"],
    "Deep Learning": [r"(?<![a-zA-Z0-9])(?:deep\s*learning|\bdl\b)(?![a-zA-Z0-9])"],
    "NLP": [r"(?<![a-zA-Z0-9])(?:natural\s*language\s*processing|\bnlp\b)(?![a-zA-Z0-9])"],
    "Computer Vision": [r"(?<![a-zA-Z0-9])(?:computer\s*vision|\bcv\b)(?![a-zA-Z0-9])"],
    "TensorFlow": [r"(?<![a-zA-Z0-9])(?:tensorflow|tf)(?![a-zA-Z0-9])"],
    "PyTorch": [r"(?<![a-zA-Z0-9])pytorch(?![a-zA-Z0-9])"],
    "Scikit-learn": [r"(?<![a-zA-Z0-9])(?:scikit-learn|scikit\s*learn|sklearn)(?![a-zA-Z0-9])"],
    "Pandas": [r"(?<![a-zA-Z0-9])pandas(?![a-zA-Z0-9])"],
    "NumPy": [r"(?<![a-zA-Z0-9])numpy(?![a-zA-Z0-9])"],
    "Matplotlib": [r"(?<![a-zA-Z0-9])matplotlib(?![a-zA-Z0-9])"],
    "Seaborn": [r"(?<![a-zA-Z0-9])seaborn(?![a-zA-Z0-9])"],
    "Streamlit": [r"(?<![a-zA-Z0-9])streamlit(?![a-zA-Z0-9])"],
    "OpenCV": [r"(?<![a-zA-Z0-9])opencv(?![a-zA-Z0-9])"],
}

# Precompile all regex patterns for efficient matching
_COMPILED_SKILLS = {
    skill_name: [re.compile(pat, re.IGNORECASE) for pat in patterns]
    for skill_name, patterns in SKILLS_DATABASE.items()
}


def extract_skills(text: str) -> List[str]:
    """
    Extract technical and domain skills from resume text.

    Uses case-insensitive pattern matching against the curated skills database,
    preventing duplicate entries and preserving canonical naming.

    Args:
        text: Normalized text from the resume.

    Returns:
        Sorted list of unique detected skill names.
    """
    if not text:
        return []

    detected_skills: Set[str] = set()

    for skill_name, patterns in _COMPILED_SKILLS.items():
        for pattern in patterns:
            if pattern.search(text):
                detected_skills.add(skill_name)
                break  # Matched this skill, continue to next skill

    # Return sorted list for consistent, deterministic output
    return sorted(list(detected_skills))
