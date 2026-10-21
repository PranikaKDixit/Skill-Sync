"""
Semantic similarity using Sentence-BERT (all-MiniLM-L6-v2).

Model is lazy-loaded on first call to avoid startup delay.
Downloads ~22MB on first use, then cached in ~/.cache/.
"""
import numpy as np
from typing import Dict

_model = None


def _get_model():
    """Lazy-load SBERT model. Thread-safe enough for single-process FastAPI."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def compute_semantic_similarity(text1: str, text2: str) -> float:
    """
    Calculate semantic similarity using Sentence-BERT.

    Returns a float between 0.0 and 1.0.
    """

    # Handle None and empty inputs
    text1 = (text1 or "").strip()
    text2 = (text2 or "").strip()

    if not text1 or not text2:
        return 0.0

    model = _get_model()

    embeddings = model.encode(
        [text1, text2],
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    similarity = float(
        np.dot(embeddings[0], embeddings[1])
    )

    return max(0.0, min(1.0, similarity))

def compute_section_similarities(
    resume_sections: Dict[str, str], jd_text: str
) -> Dict[str, float]:
    """
    Compute semantic similarity of each resume section against the JD.
    Returns {section_name: similarity} with values in [0.0, 1.0].
    """
    if not resume_sections:
        return {}

    if not jd_text or not jd_text.strip():
        return {name: 0.0 for name in resume_sections}
    model = _get_model()
    results = {}

    # Encode JD once
    jd_emb = model.encode(
        [jd_text], normalize_embeddings=True, show_progress_bar=False
    )[0]

    for section_name, section_text in resume_sections.items():
        if not section_text or not section_text.strip():
            results[section_name] = 0.0
            continue
        sec_emb = model.encode(
            [section_text], normalize_embeddings=True, show_progress_bar=False
        )[0]
        sim = float(np.dot(jd_emb, sec_emb))
        results[section_name] = max(0.0, min(1.0, sim))

    return results


