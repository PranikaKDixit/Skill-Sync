"""
train.py — Placeholder for model training.

Currently unused. This file exists for future use:
- Module 3: SBERT model fine-tuning (if needed)
- Module 4: Evaluation pipeline entry point

The ml/Dockerfile (now deleted) previously referenced this file.
All matching currently uses pretrained models and rule-based logic.
"""


"""
Train the learned scoring model.

Loads 100 labeled pairs, extracts 7 features each, trains a
GradientBoostingRegressor to predict human match scores.

Run: python -m ml.train
Output: ml/models/scorer.pkl
"""
import csv
import pickle
import numpy as np
from pathlib import Path

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from scipy.stats import pearsonr, spearmanr

from ml.feature_extractor import extract_features, FEATURE_NAMES


def load_dataset(csv_path: str):
    resumes, jds, scores = [], [], []
    with open(csv_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            resumes.append(row["resume_text"])
            jds.append(row["jd_text"])
            scores.append(float(row["human_score"]))
    return resumes, jds, np.array(scores)


def main():
    project_root = Path(__file__).parent.parent
    csv_path = project_root / "data" / "evaluation_dataset.csv"
    model_dir = project_root / "ml" / "models"
    model_path = model_dir / "scorer.pkl"

    if not csv_path.exists():
        print(f"Dataset not found: {csv_path}")
        print("Run first: python data/generate_dataset.py")
        return

    print("Loading dataset...")
    resumes, jds, scores = load_dataset(str(csv_path))
    print(f"  {len(resumes)} pairs, score range: "
          f"{scores.min():.1f} - {scores.max():.1f}")

    print("Extracting features (first run downloads SBERT ~22MB)...")
    X = np.array([extract_features(r, j) for r, j in zip(resumes, jds)])
    y = scores / 100.0  # normalize to [0, 1]
    print(f"  Feature matrix: {X.shape}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")

    print("Training GradientBoostingRegressor...")
    model = GradientBoostingRegressor(
        n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred = np.clip(model.predict(X_test), 0, 1)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    pearson = pearsonr(y_test, y_pred)[0]
    spearman = spearmanr(y_test, y_pred)[0]

    print("\n=== Test Set Results ===")
    print(f"  MAE:      {mae:.4f}")
    print(f"  R2:       {r2:.4f}")
    print(f"  Pearson:  {pearson:.4f}")
    print(f"  Spearman: {spearman:.4f}")

    print("\n=== Feature Importances (what the model learned) ===")
    for name, imp in sorted(
        zip(FEATURE_NAMES, model.feature_importances_), key=lambda x: -x[1]
    ):
        bar = "#" * int(imp * 40)
        print(f"  {name:25s} {imp:.3f} {bar}")

    model_dir.mkdir(parents=True, exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"\nModel saved -> {model_path}")
    print("You can now use mode='learned' in the API.")


if __name__ == "__main__":
    main()