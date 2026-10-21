import re
from typing import Dict, List, Any, Optional
from ml.context_extractor import analyze_skill_contexts

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ml.skills_database import SKILLS as SKILLS_DATABASE, SKILL_ALIASES
from ml.skill_ontology import get_category, get_all_categories
from ml.skill_inference import infer_skills, combine_skills
from ml.credibility_scorer import (
    score_credibility,
    credibility_weighted_match_score,
    credibility_label,
)
from ml.semantic_matcher import (
    compute_semantic_similarity,
    compute_section_similarities,
)
from pdf_parsing.section_detector import get_section_weights


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    if text is None:
        return ""

    return text.lower().strip()

def _extract_skills(text: str) -> set:
    """Extract known skills from text using the skills database."""
    text_lower = _normalize(text)
    found = set()

    for skill in SKILLS_DATABASE:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.add(skill)

    # Check aliases
    for alias, canonical in SKILL_ALIASES.items():
        pattern = r"\b" + re.escape(alias) + r"\b"
        if re.search(pattern, text_lower):
            found.add(canonical)

    return found


def _keyword_score(resume: str, jd: str) -> float:
    """Simple keyword overlap score (0-100)."""
    resume_words = set(_normalize(resume).split())
    jd_words = set(_normalize(jd).split())
    if not jd_words:
        return 0.0
    overlap = resume_words & jd_words
    return min(100.0, (len(overlap) / len(jd_words)) * 100)


def _skill_overlap_score(resume_skills: set, jd_skills: set) -> float:
    """Skill overlap as percentage of JD skills (0-100)."""
    if not jd_skills:
        return 0.0
    matched = resume_skills & jd_skills
    return min(100.0, (len(matched) / len(jd_skills)) * 100)


def _tfidf_score(resume: str, jd: str) -> float:
    """TF-IDF cosine similarity (0-100)."""

    resume = _normalize(resume)
    jd = _normalize(jd)

    if not resume or not jd:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000
        )

        vectors = vectorizer.fit_transform([resume, jd])

        similarity = cosine_similarity(
            vectors[0:1],
            vectors[1:2]
        )[0][0]

        return min(100.0, similarity * 100)

    except ValueError:
        return 0.0

# ---------------------------------------------------------------------------
# Baseline Mode (original 40/40/20)
# ---------------------------------------------------------------------------

def _calculate_baseline(resume_text: str, jd_text: str) -> Dict[str, Any]:
    """Fast baseline matching — no ML models, no inference."""
    resume_skills = _extract_skills(resume_text)
    jd_skills = _extract_skills(jd_text)

    kw = _keyword_score(resume_text, jd_text)
    sk = _skill_overlap_score(resume_skills, jd_skills)
    tf = _tfidf_score(resume_text, jd_text)

    score = 0.40 * kw + 0.40 * sk + 0.20 * tf

    return {
        "score": round(min(100, max(0, score)), 1),
        "breakdown": {
            "keyword_match": round(kw * 0.40, 1),
            "skill_match": round(sk * 0.40, 1),
            "tfidf_similarity": round(tf * 0.20, 1),
        },
        "matched_skills": sorted(resume_skills & jd_skills),
        "missing_skills": sorted(jd_skills - resume_skills),
        "mode": "baseline",
    }


# ---------------------------------------------------------------------------
# Enhanced Mode (inference + credibility + SBERT + sections)
# ---------------------------------------------------------------------------

def _calculate_enhanced(
    resume_text: str,
    jd_text: str,
    resume_sections: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Full enhanced matching with:
    - Ontology-based skill inference
    - Credibility-weighted scoring
    - SBERT semantic similarity
    - Section-aware weighting
    """
    resume_sections = resume_sections or {"other": resume_text}

    # 1. Extract explicit skills
    resume_explicit = _extract_skills(resume_text)
    jd_skills = _extract_skills(jd_text)

    # 2. Infer implicit skills from resume
    inferred = infer_skills(resume_explicit)
    all_resume_skills = combine_skills(resume_explicit, inferred)

    # 3. Inference-aware skill match (0-100)
    if jd_skills:
        matched = all_resume_skills & jd_skills
        inference_skill_score = min(100.0, (len(matched) / len(jd_skills)) * 100)
    else:
        matched = set()
        inference_skill_score = 0.0

    # 4. Credibility-weighted score (0-100)
    context_data = analyze_skill_contexts(resume_text, all_resume_skills)
    resume_credibility = score_credibility(
        resume_explicit, inferred, context_data
    )
    credibility_details = {
        skill: {
            **resume_credibility[skill],
            "label": credibility_label(resume_credibility[skill]["score"]),
        }
        for skill in jd_skills
        if skill in resume_credibility
    }

    cred_score = credibility_weighted_match_score(
        jd_skills, credibility_details
    )

    # 5. SBERT semantic similarity (0-100)
    semantic_raw = compute_semantic_similarity(resume_text, jd_text)
    semantic_score = semantic_raw * 100

    # 6. TF-IDF (0-100)
    tf = _tfidf_score(resume_text, jd_text)

    # 7. Keyword (0-100)
    kw = _keyword_score(resume_text, jd_text)

    # 8. Section-weighted semantic (0-100)
    section_sims = compute_section_similarities(resume_sections, jd_text)
    weights = get_section_weights()
    if section_sims:
        total_weight = sum(
            weights.get(name, 0.4) for name in section_sims
        )
        if total_weight > 0:
            section_score = (
                sum(
                    sim * weights.get(name, 0.4)
                    for name, sim in section_sims.items()
                )
                / total_weight
                * 100
            )
        else:
            section_score = 0.0
    else:
        section_score = 0.0

    # --- Final weighted combination ---
    final_score = (
        0.25 * inference_skill_score
        + 0.25 * semantic_score
        + 0.20 * cred_score
        + 0.15 * tf
        + 0.10 * kw
        + 0.05 * section_score
    )

    # Build inferred skills list for response
    inferred_list = []
    for skill, info in sorted(
        inferred.items(), key=lambda x: x[1]["confidence"], reverse=True
    ):
        inferred_list.append({
            "skill": skill,
            "confidence": round(info["confidence"], 2),
            "confidence_label": info.get("confidence_label", "Medium"),
            "evidence": info["evidence"],
            "category": get_category(skill),
        })

    # Skill category coverage
    category_coverage = {}
    for cat in get_all_categories():
        cat_jd = [s for s in jd_skills if get_category(s) == cat]
        cat_resume = [s for s in all_resume_skills if get_category(s) == cat]
        if cat_jd:
            cat_matched = [s for s in cat_jd if s in cat_resume]
            category_coverage[cat] = {
                "required": len(cat_jd),
                "possessed": len(cat_matched),
                "coverage": round(len(cat_matched) / len(cat_jd) * 100, 1),
            }

    return {
        "score": round(min(100, max(0, final_score)), 1),
        "breakdown": {
            "skill_inference": round(inference_skill_score * 0.25, 1),
            "semantic_similarity": round(semantic_score * 0.25, 1),
            "credibility_weighted": round(cred_score * 0.20, 1),
            "tfidf_similarity": round(tf * 0.15, 1),
            "keyword_match": round(kw * 0.10, 1),
            "section_weighted": round(section_score * 0.05, 1),
        },
        "matched_skills": sorted(matched),
        "missing_skills": sorted(jd_skills - all_resume_skills),
        "mode": "enhanced",
        "inferred_skills": inferred_list,
        "credibility": {
            skill: {
                "score": round(details["score"], 2),
                "label": details["label"],
                "source": details["source"],
                "signals": details["signals"],
                "category": get_category(skill),
            }
            for skill, details in credibility_details.items()
        },
        "skill_categories": category_coverage,
        "section_similarities": {
            name: round(sim, 3) for name, sim in section_sims.items()
        },
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def calculate_match(
    resume_text: str,
    jd_text: str,
    mode: str = "baseline",
    resume_sections=None,
) -> Dict[str, Any]:
    """Dispatches to baseline, enhanced, or learned mode."""
    if mode == "enhanced":
        return _calculate_enhanced(resume_text, jd_text, resume_sections)

    if mode == "learned":
        from ml.learned_scorer import is_model_available, predict_score
        if not is_model_available():
            result = _calculate_enhanced(
                resume_text, jd_text, resume_sections
            )
            result["mode"] = "learned"
            result["warning"] = (
                "Model not trained yet. Falling back to enhanced. "
                "Run: python -m ml.train"
            )
            return result
        details = _calculate_enhanced(
            resume_text, jd_text, resume_sections
        )
        details["score"] = predict_score(
            resume_text, jd_text, resume_sections
        )
        details["mode"] = "learned"
        return details

    return _calculate_baseline(resume_text, jd_text)

# ---------------------------------------------------------------------------
# Backward Compatibility — Original Matching Functions
# ---------------------------------------------------------------------------

def keyword_match(resume_text: str, jd_text: str) -> float:
    """Calculate keyword overlap percentage."""
    return _keyword_score(resume_text, jd_text)


def skill_match(resume_text: str, jd_text: str) -> float:
    """Calculate skill overlap percentage."""
    resume_skills = _extract_skills(resume_text)
    jd_skills = _extract_skills(jd_text)

    return _skill_overlap_score(resume_skills, jd_skills)


def tfidf_match(resume_text: str, jd_text: str) -> float:
    """Calculate TF-IDF similarity percentage."""
    return _tfidf_score(resume_text, jd_text)


def extract_skills(text: str) -> set:
    """Extract technical skills from text."""
    return _extract_skills(text)

# --------------------------------------------------
# Token-Based Cosine Similarity
# --------------------------------------------------

from collections import Counter
from math import sqrt


def _token_cosine(tokens_a, tokens_b):
    """
    Calculate cosine similarity between two token collections.

    Returns:
        Float between 0.0 and 1.0.
    """

    if not tokens_a or not tokens_b:
        return 0.0

    counter_a = Counter(tokens_a)
    counter_b = Counter(tokens_b)

    common_tokens = counter_a.keys() & counter_b.keys()

    dot_product = sum(
        counter_a[token] * counter_b[token]
        for token in common_tokens
    )

    magnitude_a = sqrt(
        sum(count * count for count in counter_a.values())
    )

    magnitude_b = sqrt(
        sum(count * count for count in counter_b.values())
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    similarity = dot_product / (magnitude_a * magnitude_b)

    return max(0.0, min(1.0, similarity))

# --------------------------------------------------
# Text Tokenization
# --------------------------------------------------

def _tokens(text: str) -> list:
    """
    Convert text into lowercase tokens.

    Example:
        "Python Django Developer!"
        -> ["python", "django", "developer"]
    """

    if not text:
        return []

    return re.findall(r"\b\w+\b", text.lower())