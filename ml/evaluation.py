"""
Evaluation framework — compares all matching modes against human labels.
Metrics: Pearson, Spearman, MAE, RMSE, Precision@5, NDCG@5.
Statistical test: paired t-test between enhanced and learned.

Run: python -m ml.evaluation
"""
import csv
import numpy as np
from pathlib import Path
from scipy.stats import pearsonr, spearmanr, ttest_rel
from sklearn.metrics import mean_absolute_error, mean_squared_error


def load_dataset(csv_path):
    resumes, jds, scores = [], [], []
    with open(csv_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            resumes.append(row["resume_text"])
            jds.append(row["jd_text"])
            scores.append(float(row["human_score"]))
    return resumes, jds, np.array(scores)


def precision_at_k(human, predicted, k=5):
    k = min(k, len(human))
    h_top = set(np.argsort(human)[-k:])
    p_top = set(np.argsort(predicted)[-k:])
    return len(h_top & p_top) / k


def ndcg_at_k(human, predicted, k=5):
    k = min(k, len(human))
    ideal = np.argsort(human)[::-1][:k]
    ideal_dcg = sum(human[ideal[i]] / np.log2(i + 2) for i in range(k))
    pred = np.argsort(predicted)[::-1][:k]
    pred_dcg = sum(human[pred[i]] / np.log2(i + 2) for i in range(k))
    return pred_dcg / ideal_dcg if ideal_dcg > 0 else 0.0


def evaluate_mode(human, predicted, name):
    return {
        "mode": name,
        "pearson": round(pearsonr(human, predicted)[0], 3),
        "spearman": round(spearmanr(human, predicted)[0], 3),
        "mae": round(mean_absolute_error(human, predicted), 2),
        "rmse": round(np.sqrt(mean_squared_error(human, predicted)), 2),
        "p@5": round(precision_at_k(human, predicted), 3),
        "ndcg@5": round(ndcg_at_k(human, predicted), 3),
    }


def run_full_evaluation():
    from ml.matching_engine import calculate_match, _keyword_score
    from ml.learned_scorer import is_model_available, predict_score
    from pdf_parsing.section_detector import detect_sections

    csv_path = Path(__file__).parent.parent / "data" / "evaluation_dataset.csv"
    if not csv_path.exists():
        print("Dataset not found. Run: python data/generate_dataset.py")
        return

    resumes, jds, human = load_dataset(str(csv_path))
    n = len(resumes)
    print(f"Evaluating {n} pairs...\n")

    preds = {
        "random": np.random.RandomState(42).uniform(0, 100, n),
        "keyword_only": np.zeros(n),
        "baseline": np.zeros(n),
        "enhanced": np.zeros(n),
    }
    has_learned = is_model_available()
    if has_learned:
        preds["learned"] = np.zeros(n)

    for i in range(n):
        r, j = resumes[i], jds[i]
        sections = detect_sections(r)
        preds["keyword_only"][i] = _keyword_score(r, j)
        preds["baseline"][i] = calculate_match(r, j, "baseline")["score"]
        preds["enhanced"][i] = calculate_match(
            r, j, "enhanced", sections
        )["score"]
        if has_learned:
            preds["learned"][i] = predict_score(r, j, sections)
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{n} done...")

    print("\n" + "=" * 78)
    print(f"{'Mode':<15} {'Pearson':>8} {'Spearman':>9} "
          f"{'MAE':>7} {'RMSE':>7} {'P@5':>6} {'NDCG@5':>7}")
    print("-" * 78)

    for mode in ["random", "keyword_only", "baseline", "enhanced", "learned"]:
        if mode in preds:
            r = evaluate_mode(human, preds[mode], mode)
            print(f"{r['mode']:<15} {r['pearson']:>8.3f} {r['spearman']:>9.3f} "
                  f"{r['mae']:>7.2f} {r['rmse']:>7.2f} "
                  f"{r['p@5']:>6.3f} {r['ndcg@5']:>7.3f}")

    if has_learned:
        print("\n--- Statistical Significance (Enhanced vs Learned) ---")
        t, p = ttest_rel(preds["enhanced"], preds["learned"])
        print(f"  Paired t-test: t={t:.3f}, p={p:.4f}")
        if p < 0.05:
            print("  -> Significant difference (p < 0.05)")
        else:
            print("  -> No significant difference (p >= 0.05)")
            print("  -> Learned model performs comparably to hand-tuned")

    print("=" * 78)


if __name__ == "__main__":
    run_full_evaluation()