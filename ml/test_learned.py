"""Tests for learned scoring, feature extraction, and evaluation."""
import os
import pickle
import tempfile
import numpy as np
import pytest

from ml.feature_extractor import extract_features, FEATURE_NAMES
from ml.learned_scorer import predict_score

SAMPLE_RESUME = (
    "SKILLS\nPython, Django, PostgreSQL, Docker, Git\n"
    "EXPERIENCE\nBackend Developer at TechCorp\n"
    "- Built REST APIs with Django\n"
    "EDUCATION\nB.Tech CS"
)
SAMPLE_JD = (
    "Python Developer needed.\n"
    "Required: Python, Django, PostgreSQL, Docker.\n"
    "Build backend services."
)


class TestFeatureExtractor:
    def test_returns_7_features(self):
        f = extract_features(SAMPLE_RESUME, SAMPLE_JD)
        assert f.shape == (7,)

    def test_features_bounded(self):
        f = extract_features(SAMPLE_RESUME, SAMPLE_JD)
        for i, v in enumerate(f):
            assert 0.0 <= v <= 1.0, f"{FEATURE_NAMES[i]}={v} out of [0,1]"

    def test_matching_higher_than_mismatch(self):
        good_jd = "Python Django developer with PostgreSQL"
        bad_jd = "Java Spring Boot developer with Oracle"
        f_good = extract_features(SAMPLE_RESUME, good_jd)
        f_bad = extract_features(SAMPLE_RESUME, bad_jd)
        assert f_good[1] > f_bad[1]  # skill_match index

    def test_empty_inputs(self):
        f = extract_features("", "")
        assert f.shape == (7,)
        assert all(v == 0.0 for v in f)


class TestLearnedScorer:
    def test_returns_float(self):
        score = predict_score(SAMPLE_RESUME, SAMPLE_JD)
        assert isinstance(score, float)

    def test_bounded(self):
        score = predict_score(SAMPLE_RESUME, SAMPLE_JD)
        assert 0.0 <= score <= 100.0


class TestTrainingPipeline:
    def test_gbr_trains_and_predicts(self):
        from sklearn.ensemble import GradientBoostingRegressor
        X = np.random.RandomState(42).rand(10, 7)
        y = np.random.RandomState(42).rand(10)
        model = GradientBoostingRegressor(n_estimators=10, max_depth=2, random_state=42)
        model.fit(X, y)
        pred = model.predict(X[:1])
        assert pred.shape == (1,)

    def test_model_serialization(self):
        from sklearn.ensemble import GradientBoostingRegressor
        X = np.random.RandomState(42).rand(10, 7)
        y = np.random.RandomState(42).rand(10)
        model = GradientBoostingRegressor(n_estimators=5, random_state=42)
        model.fit(X, y)
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            pickle.dump(model, f)
            tmp = f.name
        try:
            with open(tmp, "rb") as f:
                loaded = pickle.load(f)
            np.testing.assert_array_almost_equal(
                model.predict(X[:1]), loaded.predict(X[:1])
            )
        finally:
            os.unlink(tmp)


class TestEvaluationMetrics:
    def test_pearson_perfect(self):
        from scipy.stats import pearsonr
        s = np.array([10, 20, 30, 40, 50])
        assert pearsonr(s, s)[0] > 0.99

    def test_mae_zero_perfect(self):
        from sklearn.metrics import mean_absolute_error
        s = np.array([10, 20, 30])
        assert mean_absolute_error(s, s) == 0.0

    def test_precision_at_k_perfect(self):
        from ml.evaluation import precision_at_k
        s = np.array([10, 20, 30, 40, 50])
        assert precision_at_k(s, s, k=3) == 1.0

    def test_ndcg_perfect(self):
        from ml.evaluation import ndcg_at_k
        s = np.array([10, 20, 30, 40, 50])
        assert ndcg_at_k(s, s, k=5) > 0.99