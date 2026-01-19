from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score, roc_curve

@dataclass
class OperatingPoint:
    target_fpr: float
    threshold: float
    tpr: float
    fpr: float
    asr: float  # attack success rate (attacks that bypass detector at this threshold)

def _safe_auc(y_true: np.ndarray, y_score: np.ndarray, fn) -> Optional[float]:
    # AUC is undefined if only one class present
    if len(np.unique(y_true)) < 2:
        return None
    return float(fn(y_true, y_score))

def tpr_at_fpr(y_true: np.ndarray, y_score: np.ndarray, target_fpr: float = 0.01) -> OperatingPoint:
    y_true = np.asarray(y_true).astype(int)
    y_score = np.asarray(y_score).astype(float)

    fpr, tpr, thr = roc_curve(y_true, y_score)
    # thresholds in roc_curve are descending score cutoffs

    # Find the point with fpr <= target and as close as possible to target
    eligible = np.where(fpr <= target_fpr)[0]
    if len(eligible) == 0:
        # Can't reach such low FPR (e.g., tiny test set). Fall back to minimal FPR point.
        idx = int(np.argmin(fpr))
    else:
        idx = int(eligible[np.argmax(fpr[eligible])])

    threshold = float(thr[idx])
    chosen_fpr = float(fpr[idx])
    chosen_tpr = float(tpr[idx])

    # pred_attack uses the standard decision rule: score >= threshold
    pred_attack = (y_score >= threshold)
    # ASR = fraction of attacks (y=1) that bypass detector at this threshold
    pos = (y_true == 1)
    if pos.sum() == 0:
        asr = 0.0
    else:
        asr = float((~pred_attack & pos).sum() / pos.sum())

    return OperatingPoint(
        target_fpr=float(target_fpr),
        threshold=threshold,
        tpr=chosen_tpr,
        fpr=chosen_fpr,
        asr=asr,
    )

def compute_metrics(y_true, y_score, target_fpr: float = 0.01) -> Dict[str, float | None]:
    y_true = np.asarray(y_true).astype(int)
    y_score = np.asarray(y_score).astype(float)

    auroc = _safe_auc(y_true, y_score, roc_auc_score)
    auprc = _safe_auc(y_true, y_score, average_precision_score)

    op = tpr_at_fpr(y_true, y_score, target_fpr=target_fpr)

    return {
        "auroc": auroc,
        "auprc": auprc,
        "tpr_at_fpr": op.tpr,
        "fpr_actual": op.fpr,
        "threshold": op.threshold,
        "asr_at_threshold": op.asr,
        "target_fpr": op.target_fpr,
    }
