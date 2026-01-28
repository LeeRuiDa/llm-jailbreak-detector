from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from sklearn.metrics import average_precision_score, roc_auc_score

REPO_ROOT = Path(__file__).resolve().parents[1]
EVAL_GRID_PATH = REPO_ROOT / "scripts" / "eval_week7_grid.py"
OUT_PATH = (
    REPO_ROOT
    / "reports"
    / "week7"
    / "locked_eval_pack"
    / "week7_norm_only"
    / "tables"
    / "week7_table_rules_baseline.md"
)

TARGET_SPLITS = {
    "test_main",
    "test_main_unicode",
    "test_main_adv2",
    "test_main_rewrite",
    "test_jbb_adv2",
}


def _parse_eval_grid_datasets(path: Path) -> List[Tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    rows: List[Tuple[str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("(\"") and "," in line:
            parts = line.strip("(),").split(",", 1)
            split = parts[0].strip().strip("\"")
            rel_path = parts[1].strip().strip("\"")
            rows.append((split, rel_path))
    return rows


def _iter_jsonl(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_no} in {path}") from exc


def _metrics_at_threshold(
    y_true: List[int], y_score: List[float], threshold: float
) -> Dict[str, float | None]:
    auroc = roc_auc_score(y_true, y_score) if len(set(y_true)) > 1 else None
    auprc = average_precision_score(y_true, y_score) if len(set(y_true)) > 1 else None
    pos = [label == 1 for label in y_true]
    neg = [label == 0 for label in y_true]
    pos_total = sum(pos)
    neg_total = sum(neg)
    pred_attack = [score >= threshold for score in y_score]
    tpr = sum(pa and p for pa, p in zip(pred_attack, pos)) / pos_total if pos_total else 0.0
    fpr = sum(pa and n for pa, n in zip(pred_attack, neg)) / neg_total if neg_total else 0.0
    asr = sum((not pa) and p for pa, p in zip(pred_attack, pos)) / pos_total if pos_total else 0.0
    return {
        "auroc": auroc,
        "auprc": auprc,
        "fpr_at_threshold": fpr,
        "tpr_at_threshold": tpr,
        "asr_at_threshold": asr,
    }


def main() -> None:
    if not EVAL_GRID_PATH.exists():
        raise FileNotFoundError(f"Missing eval grid script: {EVAL_GRID_PATH}")

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    from src.baselines.rules import RulesDetector

    datasets = [
        (split, rel_path)
        for split, rel_path in _parse_eval_grid_datasets(EVAL_GRID_PATH)
        if split in TARGET_SPLITS
    ]
    if not datasets:
        raise RuntimeError("No target splits found in eval grid.")

    det = RulesDetector()
    threshold = 0.5

    rows: List[List[str]] = []
    for split, rel_path in datasets:
        data_path = REPO_ROOT / rel_path
        if not data_path.exists():
            raise FileNotFoundError(f"Missing dataset: {data_path}")

        y_true: List[int] = []
        y_score: List[float] = []
        for row in _iter_jsonl(data_path):
            text = row.get("text")
            label = row.get("label")
            if text is None or label is None:
                raise ValueError(f"Missing text/label in {data_path}")
            y_true.append(int(label))
            y_score.append(float(det.score(text)))

        metrics = _metrics_at_threshold(y_true, y_score, threshold)
        row = [
            "rules_baseline",
            split,
            f"{metrics['auroc']:.4f}" if metrics["auroc"] is not None else "-",
            f"{metrics['auprc']:.4f}" if metrics["auprc"] is not None else "-",
            f"{threshold:.4f}",
            f"{metrics['fpr_at_threshold']:.4f}",
            f"{metrics['tpr_at_threshold']:.4f}",
            f"{metrics['asr_at_threshold']:.4f}",
        ]
        rows.append(row)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Rules baseline (fixed threshold = 0.5; no val threshold transfer)",
        "",
        "| run | split | auroc | auprc | val_threshold | fpr_at_val_threshold | tpr_at_val_threshold | asr_at_threshold |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote: {OUT_PATH}")


if __name__ == "__main__":
    main()
