"""
Loads trained GBR model and predicts match scores.
Falls back gracefully if model hasn't been trained yet.
"""
import pickle
import numpy as np
from pathlib import Path
from typing import Dict, Optional

from ml.feature_extractor import extract_features

_model = None
_model_path = Path(__file__).parent / "models" / "scorer.pkl"


def _load_model():
    global _model
    if _model is None:
        if not _model_path.exists():
            return None
        with open(_model_path, "rb") as f:
            _model = pickle.load(f)
    return _model


def is_model_available() -> bool:
    return _model_path.exists()


def predict_score(
    resume_text: str,
    jd_text: str,
    resume_sections: Optional[Dict[str, str]] = None,
) -> float:
    model = _load_model()
    if model is None:
        return 0.0
    features = extract_features(resume_text, jd_text, resume_sections)
    pred = float(model.predict(features.reshape(1, -1))[0])
    return round(max(0.0, min(1.0, pred)) * 100, 1)