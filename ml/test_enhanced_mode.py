"""Integration tests for the enhanced matching mode."""

import pytest
from ml.matching_engine import calculate_match


class TestEnhancedModeIntegration:
    """End-to-end tests for enhanced matching."""

    def test_enhanced_returns_additional_fields(self):
        resume = "Python developer with Django experience"
        job = "Looking for Python developer"
        result = calculate_match(resume, job, mode="enhanced")

        assert "inferred_skills" in result
        assert "credibility" in result
        assert "skill_categories" in result
        assert result["mode"] == "enhanced"

    def test_inferred_python_from_django(self):
        """
        The star feature: resume mentions Django and Pandas but not Python.
        System should infer Python with high confidence.
        """
        resume = """
        Senior Backend Engineer
        
        Experience:
        - Built REST APIs using Django and FastAPI
        - Developed data pipelines with Pandas and NumPy
        - Deployed ML models with scikit-learn
        """
        job = "Looking for a Python developer with web framework experience"

        result = calculate_match(resume, job, mode="enhanced")

        # Python should be matched (via inference), even though resume never says "Python"
        assert "python" in result["matched_skills"], \
            f"Python should be inferred and matched. Got matched: {result['matched_skills']}"

        # Python should be in inferred_skills
        inferred_names = [s["skill"] for s in result["inferred_skills"]]
        assert "python" in inferred_names

        # Should have high confidence
        python_entry = next(s for s in result["inferred_skills"] if s["skill"] == "python")
        assert python_entry["confidence"] >= 0.85

    def test_enhanced_breakdown_has_all_components(self):
        result = calculate_match("Python developer", "Python", mode="enhanced")
        breakdown = result["breakdown"]
        assert "keyword_match" in breakdown
        assert "skill_inference" in breakdown
        assert "credibility_weighted" in breakdown
        assert "tfidf_similarity" in breakdown
        assert "semantic_similarity" in breakdown
        assert "section_weighted" in breakdown

    def test_credibility_scores_present_for_explicit_skills(self):
        resume = "Expert Python developer with 5 years of Docker experience"
        job = "Python Docker"
        result = calculate_match(resume, job, mode="enhanced")

        assert "python" in result["credibility"]
        assert "docker" in result["credibility"]
        assert result["credibility"]["python"]["score"] > 0

    def test_skill_categories_coverage(self):
        resume = "Python, React, Docker, PostgreSQL developer"
        job = "Need: Python, React, Docker, PostgreSQL"
        result = calculate_match(resume, job, mode="enhanced")

        categories = result["skill_categories"]
        # Should have multiple categories represented
        assert len(categories) >= 2

    def test_baseline_mode_unchanged(self):
        result = calculate_match("Django developer", "Python developer", mode="baseline")
        assert result["mode"] == "baseline"
        assert "inferred_skills" not in result
        assert "credibility" not in result
        assert set(result["breakdown"]) == {
            "keyword_match",
            "skill_match",
            "tfidf_similarity",
        }

    def test_enhanced_scores_higher_when_inference_helps(self):
        """
        Resume with Django but no "Python":
        - Baseline misses Python
        - Enhanced should match via inference
        """
        resume = "Backend developer. Built REST APIs with Django, Flask, Pandas, scikit-learn."
        job = "Looking for Python developer with web experience"

        baseline = calculate_match(resume, job, mode="baseline")
        enhanced = calculate_match(resume, job, mode="enhanced")

        # Enhanced should have Python in matched (via inference)
        assert "python" in enhanced["matched_skills"]
        # Baseline should NOT have Python matched (not in resume text)
        assert "python" not in baseline["matched_skills"]