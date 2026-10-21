"""
Rule-based recommendation engine.

Generates up to 6 actionable recommendations based on match analysis.
No LLM needed — pure rule-based logic.
"""
from typing import Dict, List, Any

# Curated learning resources (no API calls, just URLs)
RESOURCES = {
    "python": {"name": "Python Official Tutorial", "url": "https://docs.python.org/3/tutorial/"},
    "django": {"name": "Django Girls Tutorial", "url": "https://tutorial.djangogirls.org/"},
    "react": {"name": "React Official Docs", "url": "https://react.dev/learn"},
    "javascript": {"name": "MDN JavaScript Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"},
    "docker": {"name": "Docker Getting Started", "url": "https://docs.docker.com/get-started/"},
    "aws": {"name": "AWS Free Tier", "url": "https://aws.amazon.com/free/"},
    "sql": {"name": "SQLBolt Interactive", "url": "https://sqlbolt.com/"},
    "git": {"name": "Git Handbook", "url": "https://docs.github.com/en/get-started/using-git"},
    "machine learning": {"name": "Andrew Ng ML Course", "url": "https://www.coursera.org/learn/machine-learning"},
    "kubernetes": {"name": "Kubernetes Basics", "url": "https://kubernetes.io/docs/tutorials/"},
    "typescript": {"name": "TypeScript Handbook", "url": "https://www.typescriptlang.org/docs/handbook/"},
    "postgresql": {"name": "PostgreSQL Tutorial", "url": "https://www.postgresqltutorial.com/"},
    "mongodb": {"name": "MongoDB University", "url": "https://learn.mongodb.com/"},
    "java": {"name": "Java Tutorials", "url": "https://docs.oracle.com/javase/tutorial/"},
    "spring boot": {"name": "Spring Guides", "url": "https://spring.io/guides"},
    "tensorflow": {"name": "TensorFlow Tutorials", "url": "https://www.tensorflow.org/tutorials"},
    "pandas": {"name": "Pandas 10min Guide", "url": "https://pandas.pydata.org/docs/user_guide/10min.html"},
    "node.js": {"name": "Node.js Docs", "url": "https://nodejs.org/en/docs"},
    "flutter": {"name": "Flutter Codelabs", "url": "https://docs.flutter.dev/codelabs"},
    "linux": {"name": "Linux Journey", "url": "https://linuxjourney.com/"},
}


def generate_recommendations(
    match_result: Dict[str, Any],
    resume_text: str,
    jd_text: str,
) -> List[Dict[str, str]]:
    """
    Generate up to 6 recommendations based on match analysis.
    Each recommendation has: title, description, priority, resource_name, resource_url.
    """
    recs = []
    breakdown = match_result.get("breakdown", {})
    missing = match_result.get("missing_skills", [])
    inferred = match_result.get("inferred_skills", [])
    credibility = match_result.get("credibility", {})
    score = match_result.get("score", 0)

    # 1. Low semantic similarity → reword resume
    semantic = breakdown.get("semantic_similarity", 0)
    if semantic < 15:
        recs.append({
            "title": "Match JD Terminology",
            "description": (
                "Your resume uses different words than the job description. "
                "Mirror the JD's language — if it says 'machine learning', "
                "don't just say 'predictive modeling'."
            ),
            "priority": "high",
            "resource_name": "",
            "resource_url": "",
        })

    # 2. Missing critical skills → learn them
    if missing:
        top_missing = missing[:2]
        resource = RESOURCES.get(top_missing[0], {})
        recs.append({
            "title": f"Learn: {', '.join(s.title() for s in top_missing)}",
            "description": (
                f"These skills are in the JD but missing from your resume. "
                f"Consider taking a course or building a project with "
                f"{top_missing[0]}."
            ),
            "priority": "high",
            "resource_name": resource.get("name", ""),
            "resource_url": resource.get("url", ""),
        })

    # 3. Low credibility → add context
    low_cred = [
        s for s, c in credibility.items()
        if c.get("score", 0) < 0.6
    ]
    if low_cred:
        recs.append({
            "title": "Strengthen Skill Evidence",
            "description": (
                f"Skills like '{low_cred[0]}' appear weakly in your resume. "
                f"Add specific projects, tools, or metrics showing how you "
                f"used them (e.g., 'Built X using {low_cred[0]} serving Y users')."
            ),
            "priority": "medium",
            "resource_name": "",
            "resource_url": "",
        })

    # 4. No inferred skills → list specific tools
    if not inferred:
        recs.append({
            "title": "List Specific Frameworks & Tools",
            "description": (
                "Your resume doesn't mention specific frameworks that would "
                "signal broader skills. For example, listing 'Django' "
                "automatically implies Python knowledge."
            ),
            "priority": "medium",
            "resource_name": "",
            "resource_url": "",
        })

    # 5. Low skill category coverage → diversify
    categories = match_result.get("skill_categories", {})
    low_cats = [
        cat for cat, info in categories.items()
        if info.get("coverage", 100) < 50 and info.get("required", 0) > 0
    ]
    if low_cats:
        recs.append({
            "title": f"Fill Gap in: {low_cats[0]}",
            "description": (
                f"You have low coverage in '{low_cats[0]}' "
                f"({categories[low_cats[0]]['coverage']}%). "
                f"Consider adding relevant projects or certifications."
            ),
            "priority": "medium",
            "resource_name": "",
            "resource_url": "",
        })

    # 6. General improvement if score is low
    if score < 40 and len(recs) < 5:
        recs.append({
            "title": "Tailor Your Resume Per Job",
            "description": (
                "Generic resumes score lower. Customize your skills section "
                "and experience bullets for each job application. "
                "Use the JD's exact keywords where truthful."
            ),
            "priority": "low",
            "resource_name": "",
            "resource_url": "",
        })

    return recs[:6]
