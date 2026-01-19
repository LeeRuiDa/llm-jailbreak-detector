from __future__ import annotations
import argparse, json, os, sys, subprocess
from datetime import datetime
from typing import Dict, Any, Iterable, Tuple
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.data.io import load_examples
from src.preprocess.unicode import normalize_text
from src.baselines.rules import RulesDetector
from src.eval.metrics import compute_metrics
from sklearn.metrics import average_precision_score, roc_auc_score

BASELINE_VERSION = "v0.2-week3"


def _infer_dataset_name(path: str) -> str:
    lowered = path.replace("\\", "/").lower()
    if "v1_adv" in lowered:
        return "v1_adv"
    if "/data/v1/" in lowered or "v1_holdout" in lowered:
        return "v1"
    if "/data/sample/" in lowered:
        return "sample"
    return os.path.basename(path)


def _get_git_commit(repo_root: str) -> str | None:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_root,
                text=True,
                stderr=subprocess.DEVNULL,
            )
            .strip()
        )
    except Exception:
        return None


def _iter_predictions(path: str) -> Iterable[Tuple[int, float]]:
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_no} in {path}: {e}") from e
            if "label" not in row or "score" not in row:
                raise ValueError(f"Missing label/score on line {line_no} in {path}")
            yield int(row["label"]), float(row["score"])


def _metrics_with_threshold(
    y_true: list[int], y_score: list[float], threshold: float
) -> Dict[str, float | None]:
    auroc = roc_auc_score(y_true, y_score) if len(set(y_true)) > 1 else None
    auprc = average_precision_score(y_true, y_score) if len(set(y_true)) > 1 else None
    pred_attack = [score >= threshold for score in y_score]
    pos = [label == 1 for label in y_true]
    neg = [label == 0 for label in y_true]
    pos_total = sum(pos)
    neg_total = sum(neg)
    tpr = sum(pa and p for pa, p in zip(pred_attack, pos)) / pos_total if pos_total else 0.0
    fpr = sum(pa and n for pa, n in zip(pred_attack, neg)) / neg_total if neg_total else 0.0
    asr = sum((not pa) and p for pa, p in zip(pred_attack, pos)) / pos_total if pos_total else 0.0
    return {
        "auroc": auroc,
        "auprc": auprc,
        "tpr_at_fpr": tpr,
        "fpr_actual": fpr,
        "threshold": float(threshold),
        "asr_at_threshold": asr,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="Path to JSONL dataset")
    ap.add_argument("--out_dir", required=True, help="Directory to write run artifacts")
    ap.add_argument("--use_unicode_preprocess", action="store_true", help="Apply Unicode preprocessing before scoring")
    ap.add_argument("--target_fpr", type=float, default=0.01)
    ap.add_argument(
        "--calibrate_on_val_predictions",
        help="Optional path to val predictions JSONL for threshold calibration.",
    )
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    data_path_lower = args.data.lower()
    if "test_main_unicode" in data_path_lower:
        split = "test_main_unicode"
    elif "test_jbb_unicode" in data_path_lower:
        split = "test_jbb_unicode"
    elif "test_jbb" in data_path_lower:
        split = "test_jbb"
    elif "test_main" in data_path_lower:
        split = "test_main"
    elif "val" in data_path_lower:
        split = "val"
    elif "train" in data_path_lower:
        split = "train"
    else:
        split = "unknown"

    # Save config
    dataset_name = _infer_dataset_name(args.data)
    git_commit = _get_git_commit(REPO_ROOT)
    config: Dict[str, Any] = {
        "data": args.data,
        "dataset_name": dataset_name,
        "split": split,
        "out_dir": args.out_dir,
        "use_unicode_preprocess": args.use_unicode_preprocess,
        "unicode": args.use_unicode_preprocess,
        "target_fpr": args.target_fpr,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "detector": "rules_v0",
        "baseline_version": BASELINE_VERSION,
    }
    if git_commit:
        config["git_commit"] = git_commit
    with open(os.path.join(args.out_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    examples = load_examples(args.data)
    det = RulesDetector()

    y_true = []
    y_score = []
    preds_path = os.path.join(args.out_dir, "predictions.jsonl")
    with open(preds_path, "w", encoding="utf-8") as f:
        for ex in examples:
            text = ex.text
            if args.use_unicode_preprocess:
                text = normalize_text(text)
            score_attack = det.score(text)
            y_true.append(ex.label)
            y_score.append(score_attack)

            f.write(json.dumps({
                "id": ex.id,
                "label": ex.label,
                "score": score_attack,
                "attack_type": ex.attack_type,
                "meta": ex.meta,
            }, ensure_ascii=False) + "\n")

    metrics: Dict[str, float | None]
    if split == "val":
        metrics = compute_metrics(y_true, y_score, target_fpr=args.target_fpr)
    elif args.calibrate_on_val_predictions:
        val_rows = list(_iter_predictions(args.calibrate_on_val_predictions))
        if not val_rows:
            raise RuntimeError("No rows found in val predictions for calibration.")
        val_labels = [row[0] for row in val_rows]
        val_scores = [row[1] for row in val_rows]
        op = compute_metrics(val_labels, val_scores, target_fpr=args.target_fpr)
        metrics = _metrics_with_threshold(y_true, y_score, op["threshold"])
        metrics["target_fpr"] = args.target_fpr
        metrics["threshold_source"] = args.calibrate_on_val_predictions
    else:
        print(
            "Warning: running on a non-val split without val calibration. "
            "Threshold metrics will be omitted."
        )
        auroc = roc_auc_score(y_true, y_score) if len(set(y_true)) > 1 else None
        auprc = average_precision_score(y_true, y_score) if len(set(y_true)) > 1 else None
        metrics = {
            "auroc": auroc,
            "auprc": auprc,
            "tpr_at_fpr": None,
            "fpr_actual": None,
            "threshold": None,
            "asr_at_threshold": None,
            "target_fpr": args.target_fpr,
            "threshold_source": None,
        }
    if metrics.get("auroc") is not None and metrics["auroc"] < 0.5:
        raise RuntimeError("Score orientation still wrong (AUROC < 0.5).")
    with open(os.path.join(args.out_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print("Wrote:", args.out_dir)
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
