"""Tests for SBERT semantic matching."""
import pytest
from ml.semantic_matcher import (
    compute_semantic_similarity,
    compute_section_similarities,
)


class TestSemanticSimilarity:
    def test_identical_texts_high_similarity(self):
        text = "Python developer with Django and REST API experience"
        sim = compute_semantic_similarity(text, text)
        assert sim > 0.95, f"Identical texts should be ~1.0, got {sim}"

    def test_similar_meaning_high_score(self):
        resume = "Built machine learning pipelines using scikit-learn"
        jd = "Experience with ML model development and data science"
        sim = compute_semantic_similarity(resume, jd)
        assert sim > 0.30, f"Semantically similar texts should score >0.30, got {sim}"

    def test_unrelated_texts_low_score(self):
        resume = "Experienced chef specializing in Italian cuisine"
        jd = "Senior Java developer with Spring Boot and microservices"
        sim = compute_semantic_similarity(resume, jd)
        assert sim < 0.35, f"Unrelated texts should score <0.35, got {sim}"

    def test_empty_text_returns_zero(self):
        assert compute_semantic_similarity("", "some text") == 0.0
        assert compute_semantic_similarity("some text", "") == 0.0
        assert compute_semantic_similarity("", "") == 0.0

    def test_whitespace_only_returns_zero(self):
        assert compute_semantic_similarity("   ", "text") == 0.0

    def test_score_bounded_zero_one(self):
        sim = compute_semantic_similarity("Python developer", "Java engineer")
        assert 0.0 <= sim <= 1.0


class TestSectionSimilarities:
    def test_returns_all_sections(self):
        sections = {
            "skills": "Python, Django, PostgreSQL",
            "experience": "Built web apps at TechCorp",
            "education": "B.Tech Computer Science",
        }
        jd = "Python web developer with Django experience"
        result = compute_section_similarities(sections, jd)
        assert set(result.keys()) == {"skills", "experience", "education"}

    def test_skills_section_most_similar(self):
        sections = {
            "skills": "Python, Django, REST API, PostgreSQL, Docker",
            "education": "B.Tech in Computer Science from XYZ University",
        }
        jd = "Python Django developer with REST API and PostgreSQL skills"
        result = compute_section_similarities(sections, jd)
        assert result["skills"] > result["education"], (
            f"Skills ({result['skills']:.3f}) should > education ({result['education']:.3f})"
        )

    def test_empty_jd(self):
        result = compute_section_similarities({"skills": "Python"}, "")
        assert result["skills"] == 0.0

    def test_empty_sections(self):
        result = compute_section_similarities({}, "Python developer")
        assert result == {}