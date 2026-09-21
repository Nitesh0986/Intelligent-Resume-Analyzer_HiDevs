"""
Text Preprocessing Module for Intelligent Resume Analyzer.

Provides sanitization, unicode normalization, and formatting cleanup for
raw text extracted from resume documents without destroying semantic structure.
"""

import re
import unicodedata
from typing import Optional


def clean_text(text: Optional[str]) -> str:
    """
    Clean and normalize raw text extracted from a resume.

    Performs the following non-destructive sanitization steps:
    1. Replaces unicode non-breaking spaces and zero-width spaces.
    2. Standardizes dashes and bullet characters.
    3. Removes non-printable control characters while preserving valid formatting.
    4. Normalizes carriage returns and multiple newlines (collapsing 3+ newlines to 2).
    5. Strips trailing whitespace per line and leading/trailing whitespace overall.

    Args:
        text: The raw string extracted from PDF or document.

    Returns:
        Cleaned, normalized string. Returns empty string if input is None.
    """
    if not text:
        return ""

    # Normalize unicode representations (NFKC handles ligatures like 'fi' -> 'fi')
    cleaned = unicodedata.normalize("NFKC", text)

    # Standardize non-breaking spaces and irregular spaces to standard space
    cleaned = re.sub(r"[\u00A0\u1680\u180E\u2000-\u200B\u202F\u205F\u3000\uFEFF]", " ", cleaned)

    # Normalize carriage returns and form feeds to newline
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n").replace("\x0c", "\n")

    # Standardize common bullet point symbols into standard dash
    cleaned = re.sub(r"[•●▪◦■\u2022\u2023\u25E6\u2043\u2219]", "- ", cleaned)

    # Standardize fancy hyphens and dashes (en-dash, em-dash, minus)
    cleaned = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2015\u2212]", "-", cleaned)

    # Normalize fancy quotes
    cleaned = re.sub(r"[\u2018\u2019\u201A\u201B]", "'", cleaned)
    cleaned = re.sub(r"[\u201C\u201D\u201E\u201F]", '"', cleaned)

    # Remove non-printable control characters, but preserve tabs and newlines
    cleaned = "".join(ch for ch in cleaned if ch in ("\n", "\t") or (ord(ch) >= 32 and ord(ch) != 127))

    # Clean horizontal whitespace per line (tabs and spaces) without stripping newlines
    lines = []
    for line in cleaned.split("\n"):
        # Collapse multiple spaces or tabs inside a line to a single space
        line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(line)

    cleaned = "\n".join(lines)

    # Collapse 3 or more consecutive newlines into 2 (preserving paragraph breaks)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()
