"""
Credibility Scorer.

Assigns a credibility score (0.0-1.0) to each detected skill based on
evidence quality. A skill that appears once in a long list gets a lower
score than a skill used across multiple projects with context.

Scoring factors:
    + Explicit mention                          → base 1.0
    + Used in action context (built with, etc.) → ×1.3
    + Mentioned multiple times                  → ×1.2 per extra mention (capped)
    + Years of experience mentioned             → ×1.4
    - Inferred (not explicit)                   → base = 0.7 × avg(evidence credibility)
    
Final score is capped at 1.0.
"""


# Scoring multipliers
BASE_EXPLICIT = 0.60
USAGE_CONTEXT_BONUS = 0.20
MULTIPLE_MENTIONS_BONUS = 0.10  # per extra mention, capped
YEARS_MENTIONED_BONUS = 0.15
MAX_MENTIONS_BONUS = 0.25  # cap on multi-mention contribution
INFERRED_BASE_MULTIPLIER = 0.75  # inferred skills start at 75% of evidence avg


def score_credibility(explicit_skills, inferred_skills, context_data):
    """
    Compute credibility scores for all skills (explicit + inferred).
    
    Args:
        explicit_skills: set of explicit skill names
        inferred_skills: dict from infer_skills() 
                         {skill: {confidence, evidence, level}}
        context_data: dict from analyze_skill_contexts()
                      {skill: {mentions, usage_contexts, years}}
    
    Returns:
        dict mapping skill → {
            "score": float (0.0-1.0),
            "source": "explicit" or "inferred",
            "signals": list of strings describing why this score was assigned,
        }
    """
    result = {}

    # ---- Score explicit skills ----
    for skill in explicit_skills:
        context = context_data.get(skill, {})
        mentions = context.get("mentions", 1)
        usage = context.get("usage_contexts", 0)
        years = context.get("years")

        score = BASE_EXPLICIT
        signals = ["explicit_mention"]

        # Usage context bonus
        if usage > 0:
            score += USAGE_CONTEXT_BONUS
            signals.append(f"used_in_context_{usage}x")

        # Multiple mentions bonus
        if mentions > 1:
            extra_mentions_bonus = min(
                (mentions - 1) * MULTIPLE_MENTIONS_BONUS,
                MAX_MENTIONS_BONUS
            )
            score += extra_mentions_bonus
            signals.append(f"mentioned_{mentions}x")

        # Years of experience bonus
        if years:
            score += YEARS_MENTIONED_BONUS
            signals.append(f"{years}_years_experience")

        # Cap at 1.0
        score = min(score, 1.0)

        result[skill] = {
            "score": round(score, 2),
            "source": "explicit",
            "signals": signals,
        }

    # ---- Score inferred skills ----
    for skill, inference_info in inferred_skills.items():
        evidence = inference_info["evidence"]
        confidence = inference_info["confidence"]

        # Average credibility of the evidence skills
        evidence_scores = [
            result[ev]["score"] for ev in evidence if ev in result
        ]

        if evidence_scores:
            avg_evidence = sum(evidence_scores) / len(evidence_scores)
        else:
            avg_evidence = BASE_EXPLICIT

        # Inferred score = inference confidence × base multiplier × avg evidence
        score = confidence * INFERRED_BASE_MULTIPLIER * avg_evidence
        score = min(round(score, 2), 1.0)

        signals = [f"inferred_from_{len(evidence)}_skills"]
        if confidence >= 0.85:
            signals.append("strong_evidence")
        elif confidence >= 0.70:
            signals.append("moderate_evidence")

        result[skill] = {
            "score": score,
            "source": "inferred",
            "signals": signals,
            "evidence": evidence,
        }

    return result


def credibility_weighted_match_score(jd_skills, candidate_credibility):
    """
    Compute a match score weighted by candidate's credibility for each skill.
    
    Args:
        jd_skills: set of skills required by the job description
        candidate_credibility: dict from score_credibility()
    
    Returns:
        float (0-100) representing weighted match percentage.
    """
    if not jd_skills:
        return 0.0

    total_credibility = 0.0
    for skill in jd_skills:
        if skill in candidate_credibility:
            total_credibility += candidate_credibility[skill]["score"]
        # Skills not possessed contribute 0

    # Max possible score = number of JD skills × 1.0
    max_possible = len(jd_skills)
    percentage = (total_credibility / max_possible) * 100

    return round(percentage, 2)


def credibility_label(score):
    """Convert a numeric credibility to a human-readable label."""
    if score >= 0.80:
        return "High"
    elif score >= 0.60:
        return "Medium"
    else:
        return "Low"