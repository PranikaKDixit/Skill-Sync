"""
Skill Inference Engine.

Given a set of explicit skills extracted from a resume, infers additional
implicit skills by walking the prerequisite ontology graph.

Example:
    explicit_skills = {"django", "pandas", "scikit-learn"}
    inferred = infer_skills(explicit_skills)
    # → {"python": {"confidence": 0.90, "evidence": ["django", "pandas", "scikit-learn"], "level": 1},
    #    "machine learning": {"confidence": 0.65, "evidence": ["scikit-learn"], "level": 1},
    #    "data science": {"confidence": 0.75, "evidence": ["pandas"], "level": 1}}
"""

from .skill_ontology import get_parents


# Confidence levels based on how many child skills support the inference
CONFIDENCE_STRONG = 0.90   # 3+ children present
CONFIDENCE_HIGH = 0.80     # 2 children present
CONFIDENCE_MEDIUM = 0.65   # 1 child present


def infer_skills(explicit_skills, max_depth=2):
    """
    Infer implicit skills from a set of explicit skills.
    
    Args:
        explicit_skills: set of lowercase canonical skill names
        max_depth: how many levels up the graph to traverse (default 2)
    
    Returns:
        dict mapping inferred_skill → {
            "confidence": float (0.0-1.0),
            "evidence": list of explicit skills that triggered this inference,
            "level": int (1 = direct parent, 2 = grandparent)
        }
        
        Does NOT include skills already in explicit_skills.
    """
    if not explicit_skills:
        return {}

    explicit_set = set(s.lower() for s in explicit_skills)
    inferred = {}

    # Track which skills to process at each depth level
    current_level_skills = explicit_set.copy()

    for depth in range(1, max_depth + 1):
        # For each unique parent skill, collect all its children present at this level
        parent_to_evidence = {}

        for skill in current_level_skills:
            for parent in get_parents(skill):
                # Don't infer skills that are already explicit
                if parent in explicit_set:
                    continue

                parent_to_evidence.setdefault(parent, []).append(skill)

        # Assign confidence based on evidence count
        for parent, evidence in parent_to_evidence.items():
            # If we already inferred this at a shallower depth, keep the stronger signal
            if parent in inferred and inferred[parent]["level"] < depth:
                continue

            confidence = _compute_confidence(len(evidence))

            # Reduce confidence for deeper inferences
            if depth > 1:
                confidence *= 0.75 ** (depth - 1)

            inferred[parent] = {
                "confidence": round(confidence, 2),
                "evidence": sorted(evidence),
                "level": depth,
            }

        # Prepare for next depth level: inferred skills become inputs
        current_level_skills = set(parent_to_evidence.keys())

        if not current_level_skills:
            break

    return inferred


def _compute_confidence(evidence_count):
    """Map number of supporting evidence skills to a confidence score."""
    if evidence_count >= 3:
        return CONFIDENCE_STRONG
    elif evidence_count == 2:
        return CONFIDENCE_HIGH
    else:
        return CONFIDENCE_MEDIUM


def combine_skills(explicit_skills, inferred_skills_dict):
    """
    Combine explicit and inferred skills into a single set for matching.
    
    Args:
        explicit_skills: set of skill names
        inferred_skills_dict: dict from infer_skills()
    
    Returns:
        set of all skills (explicit + inferred)
    """
    combined = set(explicit_skills)
    combined.update(inferred_skills_dict.keys())
    return combined


def confidence_label(confidence_score):
    """Convert a numeric confidence to a human-readable label."""
    if confidence_score >= 0.85:
        return "High"
    elif confidence_score >= 0.70:
        return "Medium"
    else:
        return "Low"
    