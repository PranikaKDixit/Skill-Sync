"""Tests for the skill ontology and inference engine."""

import pytest
from ml.skill_ontology import (
    PREREQUISITE_GRAPH,
    SKILL_CATEGORIES,
    CATEGORY_SKILLS,
    get_parent,
    get_parents,
    get_children,
    get_category,
    get_all_categories,
)
from ml.skill_inference import (
    infer_skills,
    combine_skills,
    confidence_label,
)


class TestOntologyStructure:
    """Verify ontology data structures are consistent."""

    def test_prerequisite_graph_is_dict(self):
        assert isinstance(PREREQUISITE_GRAPH, dict)
        assert len(PREREQUISITE_GRAPH) > 50, "Should have at least 50 relationships"

    def test_skill_categories_is_dict(self):
        assert isinstance(SKILL_CATEGORIES, dict)
        assert len(SKILL_CATEGORIES) > 50

    def test_django_maps_to_python(self):
        assert get_parent("django") == "python"

    def test_pandas_maps_to_python(self):
        assert get_parent("pandas") == "python"
        assert "data science" in get_parents("pandas")

    def test_react_maps_to_javascript(self):
        assert get_parent("react") == "javascript"

    def test_kubernetes_maps_to_docker(self):
        assert get_parent("kubernetes") == "docker"

    def test_unknown_skill_returns_none(self):
        assert get_parent("fakeskill123") is None

    def test_python_has_children(self):
        children = get_children("python")
        assert "django" in children
        assert "flask" in children
        assert "pandas" in children

    def test_python_is_in_programming_languages(self):
        assert get_category("python") == "Programming Languages"

    def test_react_is_in_web_frameworks(self):
        assert get_category("react") == "Web Frameworks"

    def test_unknown_skill_has_other_category(self):
        assert get_category("fakeskill123") == "Other"

    def test_categories_include_major_areas(self):
        categories = get_all_categories()
        assert "Programming Languages" in categories
        assert "Web Frameworks" in categories
        assert "Cloud" in categories
        assert "DevOps" in categories
        assert "Databases" in categories


class TestSkillInference:
    """Tests for the inference engine."""

    def test_django_only_infers_python(self):
        inferred = infer_skills({"django"})
        assert "python" in inferred
        assert inferred["python"]["evidence"] == ["django"]

    def test_three_python_libs_infer_python_strongly(self):
        inferred = infer_skills({"django", "pandas", "scikit-learn"})
        assert "python" in inferred
        assert inferred["python"]["confidence"] >= 0.85  # Strong signal
        assert len(inferred["python"]["evidence"]) == 3

    def test_two_python_libs_infer_python_high(self):
        inferred = infer_skills({"django", "pandas"})
        assert "python" in inferred
        assert inferred["python"]["confidence"] >= 0.75  # High signal

    def test_react_and_node_infer_javascript(self):
        inferred = infer_skills({"react", "node.js"})
        assert "javascript" in inferred
        assert "react" in inferred["javascript"]["evidence"]
        assert "node.js" in inferred["javascript"]["evidence"]

    def test_explicit_python_not_reinferred(self):
        """If Python is already explicit, don't infer it again."""
        inferred = infer_skills({"python", "django"})
        assert "python" not in inferred

    def test_empty_input_returns_empty(self):
        assert infer_skills(set()) == {}

    def test_unknown_skill_infers_nothing(self):
        inferred = infer_skills({"fakeskill"})
        assert inferred == {}

    def test_evidence_is_sorted(self):
        inferred = infer_skills({"pandas", "django", "scikit-learn"})
        assert inferred["python"]["evidence"] == sorted(inferred["python"]["evidence"])

    def test_scikit_learn_infers_ml(self):
        """scikit-learn should infer machine learning."""
        inferred = infer_skills({"scikit-learn"})
        assert "machine learning" in inferred

    def test_tensorflow_infers_deep_learning(self):
        inferred = infer_skills({"tensorflow"})
        assert "deep learning" in inferred

    def test_mysql_postgresql_infer_sql(self):
        inferred = infer_skills({"mysql", "postgresql"})
        assert "sql" in inferred

    def test_mongodb_redis_infer_nosql(self):
        inferred = infer_skills({"mongodb", "redis"})
        assert "nosql" in inferred

    def test_multi_level_inference(self):
        """
        django → python (level 1)
        scikit-learn → machine learning (level 1)
        Should allow traversal to deeper categories.
        """
        inferred = infer_skills({"django", "scikit-learn"})
        assert "python" in inferred
        assert "machine learning" in inferred


class TestCombineSkills:
    """Tests for combining explicit + inferred skills."""

    def test_combine_includes_both(self):
        explicit = {"django"}
        inferred = {"python": {"confidence": 0.65, "evidence": ["django"], "level": 1}}
        combined = combine_skills(explicit, inferred)
        assert "django" in combined
        assert "python" in combined

    def test_combine_empty_inferred(self):
        combined = combine_skills({"python"}, {})
        assert combined == {"python"}


class TestConfidenceLabel:
    """Tests for confidence label helper."""

    def test_high_confidence(self):
        assert confidence_label(0.90) == "High"
        assert confidence_label(0.85) == "High"

    def test_medium_confidence(self):
        assert confidence_label(0.75) == "Medium"
        assert confidence_label(0.70) == "Medium"

    def test_low_confidence(self):
        assert confidence_label(0.65) == "Low"
        assert confidence_label(0.50) == "Low"