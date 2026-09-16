"""Utilities for comparing resumes with job descriptions."""

import re
import math
from collections import Counter

from .skills_database import SKILL_ALIASES, SKILLS


_TOKEN_PATTERN = re.compile(r"[a-z0-9+#.-]+")
_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "in", "is", "of", "on", "or", "that", "the", "to", "with", "you",
}


def _text(value):
    return value if isinstance(value, str) else ""


def _tokens(text):
    return [token for token in _TOKEN_PATTERN.findall(_text(text).lower())
            if token not in _STOP_WORDS]


def calculate_match(resume_text, job_description):
    """Return match details with score, matched skills, and missing skills."""
    keyword_score = keyword_match(resume_text, job_description)
    skill_score = skill_match(resume_text, job_description)
    tfidf_score = tfidf_match(resume_text, job_description)
    
    overall_score = round(keyword_score * 0.4 + skill_score * 0.4 + tfidf_score * 0.2, 2)
    
    # Extract skills
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)
    
    matched_skills = list(resume_skills & job_skills)
    missing_skills = list(job_skills - resume_skills)
    
    # Return dictionary format expected by backend
    return {
        "score": overall_score,
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills)
    }


def keyword_match(resume_text, job_text):
    """Measure the percentage of job-description keywords found in a resume."""
    job_tokens = set(_tokens(job_text))
    resume_tokens = set(_tokens(resume_text))
    if not job_tokens:
        return 0.0
    return round(len(job_tokens & resume_tokens) / len(job_tokens) * 100, 2)


def skill_match(resume_text, job_text):
    """Measure how many skills requested by a job appear in the resume."""
    required_skills = extract_skills(job_text)
    if not required_skills:
        return 0.0
    return round(len(required_skills & extract_skills(resume_text)) /
                 len(required_skills) * 100, 2)


def tfidf_match(resume_text, job_text):
    """Return cosine similarity from TF-IDF as a percentage in the range 0..100."""
    resume = _text(resume_text).strip()
    job = _text(job_text).strip()
    if not resume or not job:
        return 0.0
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vectors = TfidfVectorizer(stop_words="english").fit_transform([resume, job])
        similarity = float(cosine_similarity(vectors[0:1], vectors[1:2])[0, 0])
    except (ImportError, OSError, ValueError):
        similarity = _token_cosine(_tokens(resume), _tokens(job))
    return round(similarity * 100, 2)


def _token_cosine(left_tokens, right_tokens):
    """Compute a dependency-free cosine similarity fallback."""
    left = Counter(left_tokens)
    right = Counter(right_tokens)
    vocabulary = set(left) | set(right)
    if not vocabulary:
        return 0.0
    left_length = math.sqrt(sum(left[token] ** 2 for token in vocabulary))
    right_length = math.sqrt(sum(right[token] ** 2 for token in vocabulary))
    if not left_length or not right_length:
        return 0.0
    dot_product = sum(left[token] * right[token] for token in vocabulary)
    return dot_product / (left_length * right_length)


def tfidf_similarity(resume_text, job_text):
    """Backward-compatible name for :func:`tfidf_match`."""
    return tfidf_match(resume_text, job_text)


def extract_skills(text):
    """Return canonical skills mentioned in text, matched case-insensitively."""
    normalized = re.sub(r"[^a-z0-9+#.-]+", " ", _text(text).lower()).strip()
    found = set()
    for skill in SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, normalized):
            found.add(skill)
    for alias, canonical in SKILL_ALIASES.items():
        pattern = r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])"
        if re.search(pattern, normalized):
            found.add(canonical)
    return found