from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import torch
from peft import PeftModel
from sklearn.metrics import average_precision_score, roc_auc_score
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.io import load_examples
from src.preprocess.unicode import normalize_text
from src.preprocess.normalize import normalize_text as normalize_infer_text


@dataclass
class Record:
    id: str
    text: str
    label: int


class TextDataset(Dataset):
    def __init__(self, rows: List[Record], tokenizer, max_length: int):
        self.rows = rows
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, idx: int) -> Dict:
        row = self.rows[idx]
        enc = self.tokenizer(
            row.text,
            truncation=True,
            max_length=self.max_length,
        )
        enc["labels"] = row.label
        enc["id"] = row.id
        return enc


def _apply_score_transform(scores_p1: List[float], score_transform: str) -> List[float]:
    if score_transform == "invert":
        return [1.0 - s for s in scores_p1]
    return list(scores_p1)


def _normalize_score_transform(value: str | None) -> str | None:
    if not value:
        return None
    lowered = str(value).strip().lower()
    if lowered in {"identity", "p1", "p_attack", "score"}:
        return "identity"
    if lowered in {"invert", "1-p1", "1-p_attack", "1-score"}:
        return "invert"
    return None


def _auc_stats(y_true: List[int], y_score: List[float]) -> Tuple[float | None, float | None, bool]:
    if len(set(y_true)) < 2:
        return None, None, False
    auc = float(roc_auc_score(y_true, y_score))
    inv_auc = float(roc_auc_score(y_true, [1.0 - s for s in y_score]))
    inverted = auc < 0.5 and inv_auc > 0.8
    return auc, inv_auc, inverted


def _load_config(run_dir: Path) -> Dict:
    cfg_path = run_dir / "config.json"
    if not cfg_path.exists():
        raise FileNotFoundError(f"Missing config.json in {run_dir}")
    with cfg_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _require_score_transform(cfg: Dict) -> str:
    score_transform = _normalize_score_transform(cfg.get("score_transform"))
    if not score_transform:
        raise RuntimeError(
            "Missing score_transform in config.json. Regenerate val artifacts with train_lora.py before evaluation."
        )
    return score_transform


def _load_val_threshold(cfg: Dict) -> float | None:
    threshold = cfg.get("val_threshold")
    if threshold is None:
        return None
    return float(threshold)


def _load_tokenizer(run_dir: Path, backbone: str):
    adapter_dir = run_dir / "lora_adapter"
    try:
        if adapter_dir.exists():
            return AutoTokenizer.from_pretrained(adapter_dir, use_fast=True)
        if (run_dir / "tokenizer.json").exists():
            return AutoTokenizer.from_pretrained(run_dir, use_fast=True)
        return AutoTokenizer.from_pretrained(backbone, use_fast=True)
    except Exception as exc:
        print(f"Warning: fast tokenizer failed ({exc}); falling back to slow tokenizer.")
        if adapter_dir.exists():
            return AutoTokenizer.from_pretrained(adapter_dir, use_fast=False)
        if (run_dir / "tokenizer.json").exists():
            return AutoTokenizer.from_pretrained(run_dir, use_fast=False)
        return AutoTokenizer.from_pretrained(backbone, use_fast=False)


def _load_model(run_dir: Path, backbone: str):
    base = AutoModelForSequenceClassification.from_pretrained(backbone, num_labels=2)
    adapter_dir = run_dir / "lora_adapter"
    if not adapter_dir.exists():
        raise FileNotFoundError(f"Missing adapter at {adapter_dir}")
    model = PeftModel.from_pretrained(base, adapter_dir)
    return model


def _load_records(path: Path, use_unicode: bool, normalize_infer: bool, normalize_drop_mn: bool) -> List[Record]:
    examples = load_examples(str(path))
    rows: List[Record] = []
    for ex in examples:
        text = normalize_text(ex.text) if use_unicode else ex.text
        if normalize_infer:
            text = normalize_infer_text(text, remove_cf=True, remove_mn=normalize_drop_mn)
        rows.append(Record(id=ex.id, text=text, label=int(ex.label)))
    return rows


def _collate_with_extras(features: List[Dict], data_collator) -> Dict:
    tensor_keys = {"input_ids", "attention_mask", "token_type_ids", "labels", "label"}
    extras = {}
    for key in list(features[0].keys()):
        if key not in tensor_keys:
            extras[key] = [f.pop(key) for f in features]
    batch = data_collator(features)
    batch.update(extras)
    return batch


def _compute_metrics_with_threshold(
    y_true: List[int],
    y_score: List[float],
    threshold: float,
    target_fpr: float,
) -> Dict[str, float | None]:
    y_true_arr = np.asarray(y_true, dtype=int)
    y_score_arr = np.asarray(y_score, dtype=np.float32)
    if len(np.unique(y_true_arr)) > 1:
        auroc = float(roc_auc_score(y_true_arr, y_score_arr))
        auprc = float(average_precision_score(y_true_arr, y_score_arr))
    else:
        auroc = None
        auprc = None
    pred_attack = y_score_arr >= threshold
    pos = y_true_arr == 1
    neg = y_true_arr == 0
    tpr = float((pred_attack & pos).sum() / pos.sum()) if pos.sum() else 0.0
    fpr = float((pred_attack & neg).sum() / neg.sum()) if neg.sum() else 0.0
    asr = float((~pred_attack & pos).sum() / pos.sum()) if pos.sum() else 0.0
    return {
        "auroc": auroc,
        "auprc": auprc,
        "tpr_at_fpr": tpr,
        "fpr_actual": fpr,
        "threshold": float(threshold),
        "val_threshold": float(threshold),
        "tpr_at_val_threshold": tpr,
        "fpr_at_val_threshold": fpr,
        "asr_at_threshold": asr,
        "target_fpr": float(target_fpr),
    }


def _compute_metrics_no_threshold(y_true: List[int], y_score: List[float]) -> Dict[str, float | None]:
    y_true_arr = np.asarray(y_true, dtype=int)
    y_score_arr = np.asarray(y_score, dtype=np.float32)
    if len(np.unique(y_true_arr)) > 1:
        auroc = float(roc_auc_score(y_true_arr, y_score_arr))
        auprc = float(average_precision_score(y_true_arr, y_score_arr))
    else:
        auroc = None
        auprc = None
    return {
        "auroc": auroc,
        "auprc": auprc,
        "tpr_at_fpr": None,
        "fpr_actual": None,
        "threshold": None,
        "val_threshold": None,
        "tpr_at_val_threshold": None,
        "fpr_at_val_threshold": None,
        "asr_at_threshold": None,
        "target_fpr": None,
    }


def _write_predictions(path: Path, ids: Iterable[str], y_true: Iterable[int], y_score: Iterable[float]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for ex_id, y, s in zip(ids, y_true, y_score):
            f.write(json.dumps({"id": ex_id, "label": int(y), "score": float(s)}) + "\n")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Evaluate a saved LoRA run on a new dataset split.")
    ap.add_argument("--run_dir", required=True, help="Path to run directory (runs/lora_v1_*)")
    ap.add_argument("--data", required=True, help="Path to dataset jsonl")
    ap.add_argument("--split_name", required=True, help="Split name for outputs (e.g., test_main_unicode)")
    ap.add_argument("--target_fpr", type=float, default=0.01)
    ap.add_argument("--batch_size", type=int, default=16)
    ap.add_argument("--num_workers", type=int, default=0)
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--fail_if_inverted", action="store_true", help="Fail if scores appear inverted.")
    ap.add_argument(
        "--normalize_infer",
        action="store_true",
        help="Apply NFKC + strip Cf (and optionally Mn) at inference time.",
    )
    ap.add_argument(
        "--normalize_drop_mn",
        action="store_true",
        help="When --normalize_infer is set, also drop Mn characters.",
    )
    ap.set_defaults(fail_if_inverted=False)
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir)
    data_path = Path(args.data)
    split_name = args.split_name

    cfg = _load_config(run_dir)
    backbone = cfg.get("backbone") or cfg.get("model_name")
    if not backbone:
        raise KeyError("Missing backbone/model_name in run config.json.")

    use_unicode = bool(cfg.get("unicode", False))
    tokenizer = _load_tokenizer(run_dir, backbone)
    model = _load_model(run_dir, backbone)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()

    score_transform = _require_score_transform(cfg)
    val_threshold = _load_val_threshold(cfg)
    target_fpr = float(cfg.get("target_fpr", args.target_fpr))
    if val_threshold is None:
        print("Warning: missing val_threshold in config.json; writing AUROC/AUPRC only.")
    print(
        "Using score_transform="
        f"{score_transform} unicode_preprocess={bool(cfg.get('unicode', False))}"
    )
    max_length = int(cfg.get("max_length", 256))

    rows = _load_records(
        data_path,
        use_unicode=use_unicode,
        normalize_infer=bool(args.normalize_infer),
        normalize_drop_mn=bool(args.normalize_drop_mn),
    )
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer, return_tensors="pt")
    collate_fn = lambda feats: _collate_with_extras(feats, data_collator)  # noqa: E731
    loader = DataLoader(
        TextDataset(rows, tokenizer, max_length),
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=collate_fn,
        num_workers=args.num_workers,
    )

    all_ids: List[str] = []
    all_labels: List[int] = []
    all_scores_p1: List[float] = []
    with torch.no_grad():
        for batch in loader:
            ids = batch.pop("id")
            labels = batch.pop("labels")
            inputs = {k: v.to(device) for k, v in batch.items() if torch.is_tensor(v)}
            logits = model(**inputs).logits
            probs = torch.softmax(logits.float(), dim=-1)
            score_p1 = probs[:, 1]
            all_ids.extend(ids)
            all_labels.extend(labels.detach().cpu().tolist())
            all_scores_p1.extend(score_p1.detach().cpu().tolist())

    all_scores = _apply_score_transform(all_scores_p1, score_transform)
    if val_threshold is None:
        metrics = _compute_metrics_no_threshold(all_labels, all_scores)
    else:
        metrics = _compute_metrics_with_threshold(
            all_labels, all_scores, threshold=val_threshold, target_fpr=target_fpr
        )
    metrics["split"] = split_name
    metrics["threshold_source"] = "val" if val_threshold is not None else None
    metrics["score_is_attack_prob"] = True
    metrics["score_transform"] = score_transform
    metrics["normalize_infer"] = bool(args.normalize_infer)
    metrics["normalize_drop_mn"] = bool(args.normalize_drop_mn)

    auc, inv_auc, inverted = _auc_stats(all_labels, all_scores)
    if inverted and args.fail_if_inverted:
        raise RuntimeError(
            f"AUROC={auc:.4f} suggests inverted scores (inv_auc={inv_auc:.4f}). "
            "Check score_transform in run config."
        )
    if inverted:
        print(f"Warning: {split_name} AUROC={auc:.4f} suggests inverted scores (inv_auc={inv_auc:.4f}).")

    if auc is not None:
        if val_threshold is None:
            print(f"{split_name}: auc={auc:.4f} inv_auc={inv_auc:.4f}")
        else:
            print(
                f"{split_name}: auc={auc:.4f} inv_auc={inv_auc:.4f} "
                f"fpr@thr={metrics.get('fpr_actual'):.4f} tpr@thr={metrics.get('tpr_at_fpr'):.4f}"
            )

    suffix = "_norm" if args.normalize_infer else ""
    pred_path = run_dir / f"predictions_{split_name}{suffix}.jsonl"
    _write_predictions(pred_path, all_ids, all_labels, all_scores)

    metrics_path = run_dir / f"final_metrics_{split_name}{suffix}.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    cfg[f"{split_name}_path"] = str(data_path.resolve())
    evaluated = cfg.get("evaluated_splits")
    if isinstance(evaluated, list):
        if split_name not in evaluated:
            evaluated.append(split_name)
    else:
        cfg["evaluated_splits"] = [split_name]
    cfg["score_is_attack_prob"] = True
    cfg["score_transform"] = score_transform
    (run_dir / "config.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")

    print(f"Wrote {pred_path.name} and {metrics_path.name} in {run_dir}")


if __name__ == "__main__":
    main()
