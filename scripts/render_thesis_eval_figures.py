from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "runs" / "week7_norm_only"
OUT_DIR = ROOT / "thesis_final_tex" / "figures"

THRESHOLD = json.loads((RUN_DIR / "val_operating_point.json").read_text(encoding="utf-8"))["threshold"]


def load_predictions(split: str) -> tuple[np.ndarray, np.ndarray]:
    path = RUN_DIR / f"predictions_{split}.jsonl"
    labels: list[int] = []
    scores: list[float] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            labels.append(int(row["label"]))
            scores.append(float(row["score"]))
    return np.asarray(labels, dtype=int), np.asarray(scores, dtype=float)


def build_roc(split: str, output_name: str, title: str) -> None:
    labels, scores = load_predictions(split)
    fpr, tpr, thresholds = roc_curve(labels, scores)
    idx = int(np.argmin(np.abs(thresholds - THRESHOLD)))
    point_fpr = float(fpr[idx])
    point_tpr = float(tpr[idx])

    fig, ax = plt.subplots(figsize=(8.2, 6.0), constrained_layout=True)
    ax.plot(fpr, tpr, color="#0b6e4f", linewidth=2.2, label="ROC")
    ax.plot([0, 1], [0, 1], linestyle="--", color="#999999", linewidth=1.0)
    ax.scatter(
        [point_fpr],
        [point_tpr],
        s=80,
        color="#c1121f",
        zorder=5,
        label=f"Transferred threshold tau={THRESHOLD:.4f}",
    )
    ax.annotate(
        f"tau={THRESHOLD:.4f}\nFPR={point_fpr:.4f}, TPR={point_tpr:.4f}",
        xy=(point_fpr, point_tpr),
        xytext=(0.58, 0.16),
        textcoords="axes fraction",
        arrowprops={"arrowstyle": "->", "color": "#c1121f", "lw": 1.2},
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "#c1121f", "alpha": 0.92},
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(title)
    ax.legend(loc="lower right", frameon=True)

    inset = ax.inset_axes([0.48, 0.48, 0.45, 0.42])
    inset.plot(fpr, tpr, color="#0b6e4f", linewidth=1.7)
    inset.scatter([point_fpr], [point_tpr], s=36, color="#c1121f", zorder=5)
    inset.set_xlim(0, min(0.2, max(point_fpr * 1.25, 0.05)))
    inset.set_ylim(max(0.0, point_tpr - 0.2), 1.01)
    inset.set_title("Low-FPR view", fontsize=8)
    inset.tick_params(labelsize=7)

    fig.savefig(OUT_DIR / output_name, dpi=260)
    plt.close(fig)


def build_histogram(split: str, output_name: str, title: str) -> None:
    labels, scores = load_predictions(split)
    benign = scores[labels == 0]
    attack = scores[labels == 1]
    bins = np.linspace(0.0, 1.0, 50)

    fig, ax = plt.subplots(figsize=(8.2, 6.0), constrained_layout=True)
    ax.hist(benign, bins=bins, color="#457b9d", alpha=0.72, label="Benign", density=False)
    ax.hist(attack, bins=bins, color="#e76f51", alpha=0.52, label="Attack", density=False)
    ax.axvline(THRESHOLD, color="#c1121f", linewidth=2.0, linestyle="--", label=f"tau={THRESHOLD:.4f}")
    ax.axvspan(THRESHOLD, 1.0, color="#c1121f", alpha=0.08)
    ymax = ax.get_ylim()[1]
    ax.text(
        THRESHOLD + 0.01,
        ymax * 0.87,
        "Block region",
        color="#8d0b17",
        fontsize=9,
        rotation=90,
        va="top",
    )
    ax.set_xlabel("Attack score")
    ax.set_ylabel("Count")
    ax.set_title(title)
    ax.legend(frameon=True)

    zoom = ax.inset_axes([0.54, 0.48, 0.40, 0.38])
    zoom.hist(benign, bins=bins, color="#457b9d", alpha=0.72, density=False)
    zoom.hist(attack, bins=bins, color="#e76f51", alpha=0.52, density=False)
    zoom.axvline(THRESHOLD, color="#c1121f", linewidth=1.5, linestyle="--")
    zoom.set_xlim(max(0.0, THRESHOLD - 0.2), 1.0)
    zoom.set_title("Threshold neighborhood", fontsize=8)
    zoom.tick_params(labelsize=7)

    fig.savefig(OUT_DIR / output_name, dpi=260)
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    build_roc(
        "test_main_adv2",
        "roc_week7_norm_only_test_main_adv2.png",
        "week7_norm_only on test_main_adv2",
    )
    build_roc(
        "test_main_rewrite",
        "roc_week7_norm_only_test_main_rewrite.png",
        "week7_norm_only on test_main_rewrite",
    )
    build_roc(
        "test_jbb_adv2",
        "roc_week7_norm_only_test_jbb_adv2.png",
        "week7_norm_only on test_jbb_adv2",
    )
    build_histogram(
        "test_main_adv2",
        "hist_week7_norm_only_test_main_adv2.png",
        "Score distribution on test_main_adv2",
    )
    build_histogram(
        "test_jbb_adv2",
        "hist_week7_norm_only_test_jbb_adv2.png",
        "Score distribution on test_jbb_adv2",
    )


if __name__ == "__main__":
    main()
