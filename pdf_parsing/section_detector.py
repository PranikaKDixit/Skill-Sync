"""
Heuristic resume section detector.

Splits resume text into sections (SKILLS, EXPERIENCE, EDUCATION, PROJECTS, etc.)
by detecting ALL-CAPS headings, title-case headings, and common patterns.

No ML needed — pure regex + string heuristics.
"""
import re
from typing import Dict, List, Tuple

# Canonical section names → regex patterns that match their headings
SECTION_PATTERNS: Dict[str, List[str]] = {
    "skills": [
        r"^(technical\s+)?skills(\s*[&and]+\s*\w+)*$",
        r"^core\s+competenc",
        r"^technologies$",
        r"^tech\s+stack$",
        r"^proficien",
        r"^areas?\s+of\s+expertise$",
    ],
    "experience": [
        r"^(work|professional|relevant)\s+experience$",
        r"^experience$",
        r"^employment$",
        r"^work\s+history$",
        r"^career\s+history$",
        r"^internships?$",
    ],
    "education": [
        r"^education$",
        r"^academic\s+(background|history|qualifications)$",
        r"^qualifications$",
        r"^academic\s+details?$",
    ],
    "projects": [
        r"^(key\s+|personal\s+|academic\s+)?projects?$",
    ],
    "summary": [
        r"^(professional\s+)?(summary|profile)$",
        r"^objective$",
        r"^about(\s+me)?$",
        r"^career\s+(objective|summary)$",
    ],
    "certifications": [
        r"^certificat",
        r"^licenses?",
        r"^awards?",
        r"^achievements?$",
    ],
}

# Importance weights for section-aware scoring
SECTION_WEIGHTS: Dict[str, float] = {
    "skills": 1.0,
    "projects": 0.9,
    "experience": 0.8,
    "certifications": 0.7,
    "education": 0.6,
    "summary": 0.5,
    "other": 0.4,
}


def _clean_heading(line: str) -> str:
    """Remove decorative characters from a potential heading."""
    cleaned = line.strip()
    # Remove leading/trailing dashes, asterisks, equals, hashes
    cleaned = re.sub(r"^[\-*=#~_]+|[\-*=#~_]+$", "", cleaned)
    # Remove markdown bold markers
    cleaned = cleaned.replace("**", "").replace("__", "")
    return cleaned.strip().rstrip(":").strip()


def _is_section_heading(line: str) -> Tuple[bool, str]:
    """
    Determine if a line is a section heading.
    Returns (is_heading, canonical_section_name).
    """
    cleaned = _clean_heading(line)
    if not cleaned or len(cleaned) > 60:
        return False, ""

    alpha_chars = [c for c in cleaned if c.isalpha()]
    if len(alpha_chars) < 2:
        return False, ""

    # Check formatting signals
    upper_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
    is_all_caps = upper_ratio >= 0.8
    is_title_case = cleaned.istitle() and len(cleaned.split()) <= 5
    is_short_bold = len(cleaned.split()) <= 3 and cleaned.endswith(":")

    if not (is_all_caps or is_title_case or is_short_bold):
        return False, ""

    # Match against known patterns
    lower = cleaned.lower()
    for canonical, patterns in SECTION_PATTERNS.items():
        for pattern in patterns:
            if re.match(pattern, lower):
                return True, canonical

    return False, ""


def detect_sections(text: str) -> Dict[str, str]:
    """
    Split resume text into named sections.

    Returns dict like:
        {
            "other": "John Doe\\njohn@email.com",
            "skills": "Python, Django, Docker",
            "experience": "Software Engineer at ...",
            "education": "B.Tech CS, XYZ University"
        }
    """
    if not text or not text.strip():
        return {"other": text or ""}

    lines = text.split("\n")
    sections: Dict[str, str] = {}
    current_section = "other"
    current_lines: List[str] = []

    for line in lines:
        is_heading, section_name = _is_section_heading(line)

        if is_heading and section_name != current_section:
            # Flush previous section
            content = "\n".join(current_lines).strip()
            if content:
                existing = sections.get(current_section, "")
                sections[current_section] = (
                    f"{existing}\n{content}".strip() if existing else content
                )
            current_section = section_name
            current_lines = []
        else:
            current_lines.append(line)

    # Flush last section
    content = "\n".join(current_lines).strip()
    if content:
        existing = sections.get(current_section, "")
        sections[current_section] = (
            f"{existing}\n{content}".strip() if existing else content
        )

    return sections


def get_section_weights() -> Dict[str, float]:
    """Return importance weights for each section type."""
    return dict(SECTION_WEIGHTS)