"""
Contextual Skill Extractor.

Analyzes resume text to detect:
    - How many times each skill is mentioned
    - In what context (project description, experience bullet, skills list)
    - Years of experience with each skill (where parseable)

This feeds into the credibility scorer to produce evidence-weighted scores.
"""

import re


# Patterns that indicate a skill is being USED in a project/experience,
# not just listed
USAGE_PATTERNS = [
    r"\busing\s+{skill}\b",
    r"\bwith\s+{skill}\b",
    r"\bin\s+{skill}\b",
    r"\bbuilt\s+(?:with|using|on)\s+{skill}\b",
    r"\bdeveloped\s+(?:with|using|in)\s+{skill}\b",
    r"\bimplemented\s+(?:with|using|in)\s+{skill}\b",
    r"\bdeployed\s+(?:with|using|on)\s+{skill}\b",
    r"\bcreated\s+(?:with|using|in)\s+{skill}\b",
    r"\bexperience\s+(?:with|in)\s+{skill}\b",
    r"\bworked\s+(?:with|on)\s+{skill}\b",
    r"\bproficient\s+(?:with|in)\s+{skill}\b",
    r"\bexpert\s+(?:with|in)\s+{skill}\b",
]


# Pattern to detect years of experience with a specific skill
# Matches: "5 years of Python", "5+ years Python", "3 years experience with Docker"
YEARS_PATTERN = r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience\s+(?:with|in)\s+)?{skill}"


def count_mentions(text, skill):
    """
    Count how many times a skill is mentioned in the text.
    Uses word boundary matching to avoid false positives.
    """
    text_lower = text.lower()
    skill_escaped = re.escape(skill.lower())
    pattern = r"(?<![a-z0-9])" + skill_escaped + r"(?![a-z0-9])"
    return len(re.findall(pattern, text_lower))


def detect_usage_contexts(text, skill):
    """
    Detect how many times a skill appears in action/usage context.
    E.g., "built with Python", "deployed on AWS".
    
    Returns int count.
    """
    text_lower = text.lower()
    skill_escaped = re.escape(skill.lower())
    total = 0

    for template in USAGE_PATTERNS:
        pattern = template.format(skill=skill_escaped)
        matches = re.findall(pattern, text_lower)
        total += len(matches)

    return total


def extract_years_of_experience(text, skill):
    """
    Try to extract years of experience for a specific skill.
    
    Returns:
        int (number of years) or None if not detected.
    """
    text_lower = text.lower()
    skill_escaped = re.escape(skill.lower())
    pattern = YEARS_PATTERN.format(skill=skill_escaped)

    match = re.search(pattern, text_lower)
    if match:
        try:
            return int(match.group(1))
        except (ValueError, IndexError):
            return None

    # Also try reverse order: "Python (5 years)"
    reverse_pattern = skill_escaped + r"\s*\(\s*(\d+)\+?\s*(?:years?|yrs?)"
    match = re.search(reverse_pattern, text_lower)
    if match:
        try:
            return int(match.group(1))
        except (ValueError, IndexError):
            return None

    return None


def analyze_skill_contexts(resume_text, skills):
    """
    For each skill, analyze its context in the resume.
    
    Args:
        resume_text: full resume text
        skills: set or list of skill names to analyze
    
    Returns:
        dict mapping skill → {
            "mentions": int,
            "usage_contexts": int (times used in action phrases),
            "years": int or None,
        }
    """
    result = {}

    for skill in skills:
        mentions = count_mentions(resume_text, skill)
        if mentions == 0:
            continue

        result[skill] = {
            "mentions": mentions,
            "usage_contexts": detect_usage_contexts(resume_text, skill),
            "years": extract_years_of_experience(resume_text, skill),
        }

    return result