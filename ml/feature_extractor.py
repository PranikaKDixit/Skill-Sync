"""
Extracts 7 numerical features from each (resume, jd) pair.
These features are the INPUT to the trained regressor.
"""
import numpy as np
from typing import Dict, List, Tuple
from ml.context_extractor import analyze_skill_contexts

from ml.matching_engine import (
    _keyword_score, _skill_overlap_score,
    _tfidf_score, _extract_skills,
)
from ml.skill_inference import infer_skills, combine_skills
from ml.credibility_scorer import score_credibility
from ml.semantic_matcher import (
    compute_semantic_similarity,
    compute_section_similarities,
)
from pdf_parsing.section_detector import detect_sections, get_section_weights

FEATURE_NAMES = [
    "keyword_overlap",
    "skill_match",
    "tfidf_sim",
    "semantic_sim",
    "inferred_skill_ratio",
    "credibility_avg",
    "section_weighted",
]


def extract_features(
    resume_text: str,
    jd_text: str,
    resume_sections: Dict[str, str] = None,
) -> np.ndarray:
    if resume_sections is None:
        resume_sections = detect_sections(resume_text)

    # 1. Keyword overlap (0-1)
    kw = _keyword_score(resume_text, jd_text) / 100.0

    # 2. Skill match (0-1)
    resume_skills = _extract_skills(resume_text)
    jd_skills = _extract_skills(jd_text)
    sk = _skill_overlap_score(resume_skills, jd_skills) / 100.0

    # 3. TF-IDF (0-1)
    tf = _tfidf_score(resume_text, jd_text) / 100.0

    # 4. Semantic (0-1)
    sem = compute_semantic_similarity(resume_text, jd_text)

    # 5. Inferred skill ratio (0-1)
    inferred = infer_skills(resume_skills)
    all_skills = combine_skills(resume_skills, inferred)
    if jd_skills:
        inferred_matched = len((all_skills - resume_skills) & jd_skills)
        inferred_ratio = min(1.0, inferred_matched / len(jd_skills))
    else:
        inferred_ratio = 0.0

    # 6. Average credibility (0-1)
    if jd_skills:
        context_data = analyze_skill_contexts(resume_text, all_skills)
        credibility = score_credibility(
            resume_skills, inferred, context_data
        )
        cred_scores = [
            credibility.get(skill, {"score": 0.0})["score"]
            for skill in jd_skills
        ]
        cred_avg = float(np.mean(cred_scores))
    else:
        cred_avg = 0.0

    # 7. Section-weighted semantic (0-1)
    section_sims = compute_section_similarities(resume_sections, jd_text)
    weights = get_section_weights()
    if section_sims:
        total_w = sum(weights.get(n, 0.4) for n in section_sims)
        sec_w = (
            sum(s * weights.get(n, 0.4) for n, s in section_sims.items())
            / total_w if total_w > 0 else 0.0
        )
    else:
        sec_w = 0.0

    return np.array([kw, sk, tf, sem, inferred_ratio, cred_avg, sec_w])