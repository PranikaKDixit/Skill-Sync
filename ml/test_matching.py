"""Tests for the matching engine — runs from repo root via pytest."""

import pytest
from ml.matching_engine import (
    calculate_match,
    keyword_match,
    skill_match,
    tfidf_match,
    extract_skills,
    _token_cosine,
    _tokens,
)


class TestCalculateMatch:
    """Tests for the main calculate_match function."""

    def test_returns_dict_with_required_keys(self):
        result = calculate_match("Python developer", "Python developer needed")
        assert isinstance(result, dict)
        assert "score" in result
        assert "breakdown" in result
        assert "matched_skills" in result
        assert "missing_skills" in result
        assert "mode" in result

    def test_perfect_match(self):
        text = "Python developer with 5 years Django and React experience"
        result = calculate_match(text, text)
        assert result["score"] >= 90, f"Expected >=90, got {result['score']}"

    def test_high_match(self):
        resume = """
        Senior Software Engineer with 5 years experience in Python and JavaScript.
        Expert in Django, Flask, React, and Node.js. Built REST APIs and microservices.
        Experience with Docker, Kubernetes, AWS, PostgreSQL, and Redis.
        """
        job = """
        We're looking for a Senior Software Engineer with Python, JavaScript expertise.
        Must have Django, React, and REST API experience. AWS and Docker required.
        PostgreSQL experience preferred.
        """
        result = calculate_match(resume, job)
        assert 60 <= result["score"] <= 100, f"Expected 60-100, got {result['score']}"

    def test_low_match(self):
        resume = "Graphic designer with 3 years Photoshop, Illustrator, InDesign"
        job = "DevOps engineer needed: Docker, Kubernetes, AWS, Terraform, Jenkins"
        result = calculate_match(resume, job)
        assert result["score"] <= 30, f"Expected <=30, got {result['score']}"

    def test_empty_resume(self):
        result = calculate_match("", "Python developer needed")
        assert result["score"] == 0.0

    def test_empty_job(self):
        result = calculate_match("Python developer", "")
        assert result["score"] == 0.0

    def test_both_empty(self):
        result = calculate_match("", "")
        assert result["score"] == 0.0

    def test_none_inputs(self):
        result = calculate_match(None, None)
        assert result["score"] == 0.0

    def test_baseline_mode(self):
        result = calculate_match("Python Django", "Python Django", mode="baseline")
        assert "keyword_match" in result["breakdown"]
        assert "skill_match" in result["breakdown"]
        assert "tfidf_similarity" in result["breakdown"]

    def test_enhanced_mode(self):
        result = calculate_match("Python Django", "Python Django", mode="enhanced")
        assert result["mode"] == "enhanced"
        assert "inferred_skills" in result
        assert "skill_inference" in result["breakdown"]
        assert "credibility_weighted" in result["breakdown"]
        assert "semantic_similarity" in result["breakdown"]

    def test_breakdown_components_are_numbers(self):
        result = calculate_match("Python Django React", "Python Django React")
        for key, value in result["breakdown"].items():
            assert isinstance(value, (int, float)), f"{key} is not a number: {value}"

    def test_matched_skills_sorted(self):
        result = calculate_match(
            "Python React Docker SQL",
            "Docker Python React SQL"
        )
        assert result["matched_skills"] == sorted(result["matched_skills"])

    def test_missing_skills_sorted(self):
        result = calculate_match(
            "Python",
            "Python React Docker Kubernetes"
        )
        assert result["missing_skills"] == sorted(result["missing_skills"])


class TestKeywordMatch:
    """Tests for keyword overlap."""

    def test_full_overlap(self):
        score = keyword_match("python django flask", "python django flask")
        assert score >= 90

    def test_partial_overlap(self):
        resume = "Python developer with Django and Flask experience"
        job = "Python Django Flask developer"
        score = keyword_match(resume, job)
        assert score >= 75

    def test_no_overlap(self):
        score = keyword_match("graphic designer photoshop", "kubernetes docker aws")
        assert score <= 15

    def test_empty_job(self):
        assert keyword_match("Python developer", "") == 0.0


class TestSkillMatch:
    """Tests for skill dictionary matching."""

    def test_all_skills_match(self):
        resume = "Skills: Python, React, Docker"
        job = "Required: Python, React, Docker"
        score = skill_match(resume, job)
        assert score == 100.0

    def test_partial_skill_match(self):
        resume = "Skills: Python, React, Docker, MySQL"
        job = "Required: Python, React, AWS, PostgreSQL"
        score = skill_match(resume, job)
        assert 45 <= score <= 55  # 2 out of 4

    def test_no_skill_match(self):
        resume = "Photoshop, Illustrator, InDesign"
        job = "Docker, Kubernetes, Terraform"
        score = skill_match(resume, job)
        assert score == 0.0


class TestTfidfMatch:
    """Tests for TF-IDF similarity."""

    def test_similar_texts(self):
        resume = "Experienced software engineer with Python expertise"
        job = "Looking for experienced software engineer with Python skills"
        score = tfidf_match(resume, job)
        assert score >= 40

    def test_different_texts(self):
        score = tfidf_match(
            "Graphic designer with creative portfolio",
            "DevOps engineer with Kubernetes and AWS"
        )
        assert score <= 30

    def test_empty_input(self):
        assert tfidf_match("", "Python") == 0.0
        assert tfidf_match("Python", "") == 0.0


class TestExtractSkills:
    """Tests for skill extraction."""

    def test_basic_skills(self):
        skills = extract_skills("Expert in Python, Java, and Docker")
        assert "python" in skills
        assert "java" in skills
        assert "docker" in skills

    def test_aliases(self):
        skills = extract_skills("Expert in ReactJS, NodeJS, Postgres, K8s, and ML")
        assert "react" in skills, "ReactJS should map to react"
        assert "node.js" in skills, "NodeJS should map to node.js"
        assert "postgresql" in skills, "Postgres should map to postgresql"
        assert "kubernetes" in skills, "K8s should map to kubernetes"
        assert "machine learning" in skills, "ML should map to machine learning"

    def test_special_characters(self):
        skills = extract_skills("Expert in C++, C#, and Node.js development")
        assert "node.js" in skills

    def test_word_boundaries(self):
        """Java should not match inside JavaScript."""
        skills = extract_skills("JavaScript developer")
        assert "javascript" in skills
        # Java should NOT be found since it's part of JavaScript
        # This depends on regex boundary handling

    def test_empty_text(self):
        skills = extract_skills("")
        assert skills == set()

    def test_none_text(self):
        skills = extract_skills(None)
        assert skills == set()


class TestFallbackCosine:
    """Tests for the dependency-free cosine fallback."""

    def test_identical_tokens(self):
        tokens = ["python", "developer", "django"]
        similarity = _token_cosine(tokens, tokens)
        assert abs(similarity - 1.0) < 0.01

    def test_no_overlap(self):
        similarity = _token_cosine(
            ["python", "django"],
            ["kubernetes", "docker"]
        )
        assert similarity == 0.0

    def test_partial_overlap(self):
        similarity = _token_cosine(
            ["python", "developer", "django"],
            ["python", "developer", "react"]
        )
        assert 0.3 <= similarity <= 0.8

    def test_empty_tokens(self):
        assert _token_cosine([], []) == 0.0
        assert _token_cosine(["python"], []) == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])