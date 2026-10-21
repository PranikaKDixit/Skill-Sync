"""Tests for credibility scoring."""

import pytest
from ml.context_extractor import (
    count_mentions,
    detect_usage_contexts,
    extract_years_of_experience,
    analyze_skill_contexts,
)
from ml.credibility_scorer import (
    score_credibility,
    credibility_weighted_match_score,
    credibility_label,
)
from ml.skill_inference import infer_skills


class TestContextExtractor:

    def test_count_mentions_single(self):
        text = "I know Python programming"
        assert count_mentions(text, "python") == 1

    def test_count_mentions_multiple(self):
        text = "Python developer. Built with Python. Python expert."
        assert count_mentions(text, "python") == 3

    def test_count_mentions_zero(self):
        assert count_mentions("JavaScript developer", "python") == 0

    def test_count_mentions_word_boundary(self):
        """Should not match substring."""
        text = "Pythonic code style"  # Should not count as "python"
        count = count_mentions(text, "python")
        assert count == 0

    def test_usage_contexts_built_with(self):
        text = "Built REST APIs with Python and FastAPI"
        contexts = detect_usage_contexts(text, "python")
        assert contexts >= 1

    def test_usage_contexts_experience_with(self):
        text = "5 years of experience with Docker"
        contexts = detect_usage_contexts(text, "docker")
        assert contexts >= 1

    def test_usage_contexts_zero(self):
        text = "Skills: Python, Java"
        contexts = detect_usage_contexts(text, "python")
        assert contexts == 0

    def test_years_detection(self):
        text = "5 years of Python experience"
        years = extract_years_of_experience(text, "python")
        assert years == 5

    def test_years_detection_plus(self):
        text = "3+ years Python"
        years = extract_years_of_experience(text, "python")
        assert years == 3

    def test_years_detection_reverse(self):
        text = "Python (5 years)"
        years = extract_years_of_experience(text, "python")
        assert years == 5

    def test_years_detection_none(self):
        text = "Experienced in Python"
        assert extract_years_of_experience(text, "python") is None

    def test_analyze_contexts_full(self):
        text = """
        Senior Developer with 5 years of experience with Python.
        Built microservices using Python and deployed on AWS.
        Skills: Python, Docker, AWS.
        """
        result = analyze_skill_contexts(text, {"python", "docker", "aws"})
        assert "python" in result
        assert result["python"]["mentions"] >= 3
        assert result["python"]["years"] == 5
        assert result["python"]["usage_contexts"] >= 1


class TestCredibilityScorer:

    def test_explicit_skill_scores_above_base(self):
        explicit = {"python"}
        inferred = {}
        context = {"python": {"mentions": 1, "usage_contexts": 0, "years": None}}
        result = score_credibility(explicit, inferred, context)
        assert result["python"]["score"] >= 0.60
        assert result["python"]["source"] == "explicit"

    def test_usage_context_boosts_score(self):
        explicit = {"python"}
        inferred = {}

        context_no_usage = {"python": {"mentions": 1, "usage_contexts": 0, "years": None}}
        context_with_usage = {"python": {"mentions": 1, "usage_contexts": 2, "years": None}}

        result_a = score_credibility(explicit, inferred, context_no_usage)
        result_b = score_credibility(explicit, inferred, context_with_usage)

        assert result_b["python"]["score"] > result_a["python"]["score"]

    def test_multiple_mentions_boost_score(self):
        explicit = {"python"}
        inferred = {}

        context_single = {"python": {"mentions": 1, "usage_contexts": 0, "years": None}}
        context_multi = {"python": {"mentions": 5, "usage_contexts": 0, "years": None}}

        a = score_credibility(explicit, inferred, context_single)
        b = score_credibility(explicit, inferred, context_multi)

        assert b["python"]["score"] > a["python"]["score"]

    def test_years_boost_score(self):
        explicit = {"python"}
        inferred = {}

        no_years = {"python": {"mentions": 1, "usage_contexts": 0, "years": None}}
        with_years = {"python": {"mentions": 1, "usage_contexts": 0, "years": 5}}

        a = score_credibility(explicit, inferred, no_years)
        b = score_credibility(explicit, inferred, with_years)

        assert b["python"]["score"] > a["python"]["score"]

    def test_inferred_skill_scored_lower_than_explicit(self):
        """Inferred skills should generally score lower than strong explicit."""
        explicit = {"django", "pandas", "scikit-learn"}
        inferred = infer_skills(explicit)
        context = {s: {"mentions": 2, "usage_contexts": 1, "years": None} for s in explicit}

        result = score_credibility(explicit, inferred, context)

        # Python is inferred
        assert "python" in result
        assert result["python"]["source"] == "inferred"
        # Should score lower than its evidence
        assert result["python"]["score"] < result["django"]["score"]

    def test_score_capped_at_one(self):
        explicit = {"python"}
        inferred = {}
        context = {"python": {"mentions": 10, "usage_contexts": 10, "years": 20}}
        result = score_credibility(explicit, inferred, context)
        assert result["python"]["score"] <= 1.0

    def test_credibility_signals_present(self):
        explicit = {"python"}
        inferred = {}
        context = {"python": {"mentions": 3, "usage_contexts": 2, "years": 5}}
        result = score_credibility(explicit, inferred, context)
        signals = result["python"]["signals"]
        assert any("mention" in s for s in signals)
        assert any("year" in s for s in signals)
        assert any("context" in s for s in signals)


class TestCredibilityWeightedMatch:

    def test_perfect_match_high_credibility(self):
        job_skills = {"python", "docker"}
        credibility = {
            "python": {"score": 1.0, "source": "explicit", "signals": []},
            "docker": {"score": 1.0, "source": "explicit", "signals": []},
        }
        score = credibility_weighted_match_score(job_skills, credibility)
        assert score == 100.0

    def test_partial_match(self):
        job_skills = {"python", "docker", "kubernetes"}
        credibility = {
            "python": {"score": 1.0, "source": "explicit", "signals": []},
            "docker": {"score": 0.5, "source": "explicit", "signals": []},
            # kubernetes missing
        }
        score = credibility_weighted_match_score(job_skills, credibility)
        # 1.0 + 0.5 + 0 = 1.5 / 3 = 50%
        assert score == 50.0

    def test_no_match(self):
        job_skills = {"kubernetes"}
        credibility = {"python": {"score": 1.0, "source": "explicit", "signals": []}}
        score = credibility_weighted_match_score(job_skills, credibility)
        assert score == 0.0

    def test_empty_job_skills(self):
        assert credibility_weighted_match_score(set(), {}) == 0.0


class TestCredibilityLabel:

    def test_high_label(self):
        assert credibility_label(0.90) == "High"
        assert credibility_label(0.80) == "High"

    def test_medium_label(self):
        assert credibility_label(0.70) == "Medium"
        assert credibility_label(0.60) == "Medium"

    def test_low_label(self):
        assert credibility_label(0.50) == "Low"
        assert credibility_label(0.40) == "Low"