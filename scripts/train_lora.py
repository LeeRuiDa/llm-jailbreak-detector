from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from contextlib import nullcontext
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import torch
from peft import LoraConfig, TaskType, get_peft_model
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    get_linear_schedule_with_warmup,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.io import load_examples
from src.eval.metrics import compute_metrics, tpr_at_fpr
from src.preprocess.unicode import normalize_text

BASELINE_VERSION = "v0.3-week4"
DEFAULT_BACKBONE = "roberta-base"
DEFAULT_ATTACK_LABEL = 1  # label value corresponding to attack / unsafe
DEFAULT_MAX_LENGTH = 256
DEFAULT_WARMUP_RATIO = 0.06
TARGET_FPR = 0.01
LORA_R = 8
LORA_ALPHA = 16
LORA_DROPOUT = 0.05


def set_seed(seed: int) -> None:
    import random

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _get_git_commit(repo_root: Path) -> str | None:
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


def _sha256_file(path: Path) -> str:
    h = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _slugify_backbone(name: str) -> str:
    return name.replace("/", "-")


def _default_run_dir(backbone: str, use_unicode: bool) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    unicode_tag = "u1" if use_unicode else "u0"
    slug = _slugify_backbone(backbone)
    return Path("runs") / f"lora_v1_{slug}_{unicode_tag}_{ts}"


def _infer_dataset_name(train_path: Path) -> str:
    # Heuristic: parent directory name (e.g., data/v1/train.jsonl -> v1)
    return train_path.parent.name or "-"


def _select_lora_targets(model_type: str) -> List[str]:
    model_type = (model_type or "").lower()
    if model_type in {"roberta", "xlm-roberta"}:
        return ["q_proj", "k_proj", "v_proj"]
    if model_type in {"deberta-v2", "deberta"}:
        return ["query_proj", "key_proj", "value_proj"]
    if model_type == "distilbert":
        return ["q_lin", "v_lin"]
    return ["q_proj", "k_proj", "v_proj"]


def _extra_modules_to_save(model) -> List[str]:
    extras: List[str] = []
    if any(name.endswith("pooler") for name, _ in model.named_modules()):
        extras.append("pooler")
    return extras


@dataclass
class Record:
    id: str
    text: str
    label: int


def load_records(path: Path, use_unicode: bool) -> List[Record]:
    examples = load_examples(str(path))
    rows: List[Record] = []
    for ex in examples:
        text = normalize_text(ex.text) if use_unicode else ex.text
        rows.append(Record(id=ex.id, text=text, label=int(ex.label)))
    return rows


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
    if score_transform in {"invert", "1-p1"}:
        return [1.0 - s for s in scores_p1]
    return list(scores_p1)


def collate_with_extras(features: List[Dict], data_collator) -> Dict:
    tensor_keys = {"input_ids", "attention_mask", "token_type_ids", "labels", "label"}
    extras = {}
    for key in list(features[0].keys()):
        if key not in tensor_keys:
            extras[key] = [f.pop(key) for f in features]
    batch = data_collator(features)
    batch.update(extras)
    return batch


def write_predictions(path: Path, ids: Iterable[str], y_true: Iterable[int], y_score: Iterable[float], split: str) -> None:
    with path.open("w", encoding="utf-8") as f:
        for ex_id, y, s in zip(ids, y_true, y_score):
            f.write(json.dumps({"id": ex_id, "label": int(y), "score": float(s), "split": split}) + "\n")


def compute_split_metrics(y_true: List[int], y_score: List[float], threshold: float) -> Dict[str, float | None]:
    y_true_arr = np.asarray(y_true).astype(int)
    y_score_arr = np.asarray(y_score).astype(float)
    auroc = compute_metrics(y_true_arr, y_score_arr, target_fpr=TARGET_FPR)["auroc"] if len(set(y_true)) > 1 else None
    auprc = compute_metrics(y_true_arr, y_score_arr, target_fpr=TARGET_FPR)["auprc"] if len(set(y_true)) > 1 else None
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
    }


def build_dataloaders(
    tokenizer,
    train_rows: List[Record],
    val_rows: List[Record],
    test_main_rows: List[Record],
    test_jbb_rows: List[Record],
    batch_size: int,
    max_length: int,
    num_workers: int,
) -> Tuple[DataLoader, DataLoader, DataLoader, DataLoader]:
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer, return_tensors="pt")
    collate_fn = lambda feats: collate_with_extras(feats, data_collator)  # noqa: E731

    train_ds = TextDataset(train_rows, tokenizer, max_length)
    val_ds = TextDataset(val_rows, tokenizer, max_length)
    test_main_ds = TextDataset(test_main_rows, tokenizer, max_length)
    test_jbb_ds = TextDataset(test_jbb_rows, tokenizer, max_length)

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_fn,
        num_workers=num_workers,
    )
    eval_kwargs = {
        "batch_size": batch_size,
        "shuffle": False,
        "collate_fn": collate_fn,
        "num_workers": num_workers,
    }
    val_loader = DataLoader(val_ds, **eval_kwargs)
    test_main_loader = DataLoader(test_main_ds, **eval_kwargs)
    test_jbb_loader = DataLoader(test_jbb_ds, **eval_kwargs)
    return train_loader, val_loader, test_main_loader, test_jbb_loader


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Train LoRA classifier (Week 4 pipeline).")
    ap.add_argument("--train", required=True, help="Path to train.jsonl")
    ap.add_argument("--val", required=True, help="Path to val.jsonl")
    ap.add_argument("--test_main", required=True, help="Path to test_main.jsonl")
    ap.add_argument("--test_jbb", required=True, help="Path to test_jbb.jsonl")
    ap.add_argument("--backbone", default=DEFAULT_BACKBONE, help="HF model id for backbone (default: roberta-base)")
    ap.add_argument("--unicode_preprocess", action="store_true", help="Apply Unicode normalization to text")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch_size", type=int, default=16)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--grad_accum", type=int, default=2)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--max_length", type=int, default=DEFAULT_MAX_LENGTH)
    ap.add_argument("--out_dir", help="Optional output dir. Default uses runs/lora_v1_{backbone}_u{0/1}_{timestamp}")
    ap.add_argument("--num_workers", type=int, default=0)
    ap.add_argument("--attack_label", type=int, default=DEFAULT_ATTACK_LABEL, choices=[0, 1], help="Label value representing attacks")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    set_seed(args.seed)

    use_unicode = bool(args.unicode_preprocess)
    backbone = args.backbone.strip() or DEFAULT_BACKBONE
    run_dir = Path(args.out_dir) if args.out_dir else _default_run_dir(backbone, use_unicode)
    run_dir.mkdir(parents=True, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        tokenizer = AutoTokenizer.from_pretrained(backbone, use_fast=True)
    except Exception as exc:
        print(f"Warning: fast tokenizer failed ({exc}); falling back to slow tokenizer.")
        tokenizer = AutoTokenizer.from_pretrained(backbone, use_fast=False)
    model = AutoModelForSequenceClassification.from_pretrained(backbone, num_labels=2)

    target_modules = _select_lora_targets(model.config.model_type)
    modules_to_save = _extra_modules_to_save(model)
    lora_config = LoraConfig(
        task_type=TaskType.SEQ_CLS,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=target_modules,
        modules_to_save=modules_to_save or None,
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    model.to(device)

    train_rows = load_records(Path(args.train), use_unicode)
    val_rows = load_records(Path(args.val), use_unicode)
    test_main_rows = load_records(Path(args.test_main), use_unicode)
    test_jbb_rows = load_records(Path(args.test_jbb), use_unicode)

    train_loader, val_loader, test_main_loader, test_jbb_loader = build_dataloaders(
        tokenizer,
        train_rows,
        val_rows,
        test_main_rows,
        test_jbb_rows,
        args.batch_size,
        args.max_length,
        args.num_workers,
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    num_update_steps_per_epoch = max(1, len(train_loader) // args.grad_accum)
    total_steps = num_update_steps_per_epoch * args.epochs
    warmup_steps = int(total_steps * DEFAULT_WARMUP_RATIO)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps
    )

    use_bf16 = device == "cuda" and torch.cuda.is_bf16_supported()
    autocast_dtype = torch.bfloat16 if use_bf16 else torch.float16
    amp_context = torch.cuda.amp.autocast if device == "cuda" else nullcontext
    scaler = torch.cuda.amp.GradScaler(enabled=(device == "cuda" and not use_bf16))

    attack_class_index = 0 if args.attack_label == 0 else 1
    global_step = 0

    def train_one_epoch() -> float:
        nonlocal global_step
        model.train()
        running_loss = 0.0
        optimizer.zero_grad(set_to_none=True)

        for step, batch in enumerate(train_loader, start=1):
            batch = {k: v.to(device) for k, v in batch.items() if torch.is_tensor(v)}
            with amp_context(dtype=autocast_dtype) if device == "cuda" else nullcontext():
                out = model(**batch)
                loss = out.loss / args.grad_accum

            if scaler.is_enabled():
                scaler.scale(loss).backward()
            else:
                loss.backward()

            if step % args.grad_accum == 0:
                if scaler.is_enabled():
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                global_step += 1

            running_loss += loss.item() * args.grad_accum

        return running_loss / max(1, len(train_loader))

    def run_eval(loader: DataLoader) -> Tuple[List[str], List[int], List[float]]:
        model.eval()
        all_ids: List[str] = []
        all_labels: List[int] = []
        all_scores_p1: List[float] = []
        with torch.no_grad():
            for batch in loader:
                ids = batch.pop("id")
                labels = batch.pop("labels")
                inputs = {k: v.to(device) for k, v in batch.items() if torch.is_tensor(v)}
                logits = model(**inputs).logits
                probs = torch.softmax(logits.float(), dim=-1)  # force fp32 for stability
                score_p1 = probs[:, 1]
                all_ids.extend(ids)
                all_labels.extend(labels.detach().cpu().tolist())
                all_scores_p1.extend(score_p1.detach().cpu().tolist())
        return all_ids, all_labels, all_scores_p1

    metrics_history: List[Dict] = []
    for epoch in range(args.epochs):
        loss = train_one_epoch()
        _, y_true, y_score_p1 = run_eval(val_loader)
        epoch_metrics = compute_metrics(y_true, y_score_p1, target_fpr=TARGET_FPR)
        epoch_metrics["epoch"] = epoch
        epoch_metrics["train_loss"] = loss
        metrics_history.append(epoch_metrics)
        print(f"Epoch {epoch} loss={loss:.4f} auroc={epoch_metrics['auroc']}")

        ckpt_dir = run_dir / f"ckpt_epoch_{epoch}"
        ckpt_dir.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model_state": model.state_dict(),
                "optimizer_state": optimizer.state_dict(),
                "scheduler_state": scheduler.state_dict(),
                "scaler_state": scaler.state_dict() if scaler.is_enabled() else None,
                "epoch": epoch,
                "global_step": global_step,
            },
            ckpt_dir / "checkpoint.pt",
        )

    (run_dir / "metrics.json").write_text(json.dumps(metrics_history, indent=2), encoding="utf-8")

    # Final eval on all splits with val-derived threshold
    val_ids, val_y_true, val_y_score_p1 = run_eval(val_loader)
    val_metrics_raw = compute_metrics(val_y_true, val_y_score_p1, target_fpr=TARGET_FPR)
    val_auc = val_metrics_raw.get("auroc")
    if val_auc is None:
        print("Warning: val AUROC undefined; defaulting to identity score_transform.")
        score_transform = "identity"
    else:
        score_transform = "invert" if val_auc < 0.5 else "identity"

    val_y_score = _apply_score_transform(val_y_score_p1, score_transform)
    op = tpr_at_fpr(np.asarray(val_y_true), np.asarray(val_y_score), target_fpr=TARGET_FPR)
    op_payload = asdict(op)
    op_payload["score_is_attack_prob"] = True
    op_payload["score_transform"] = score_transform
    op_payload["score_transform_source"] = "val"
    (run_dir / "val_operating_point.json").write_text(
        json.dumps(op_payload, indent=2), encoding="utf-8"
    )

    def eval_and_save(split_name: str, ids: List[str], y_true: List[int], y_score: List[float]) -> None:
        pred_path = run_dir / f"predictions_{split_name}.jsonl"
        write_predictions(pred_path, ids, y_true, y_score, split_name)
        metrics = compute_split_metrics(y_true, y_score, op.threshold)
        metrics["target_fpr"] = TARGET_FPR
        metrics["split"] = split_name
        metrics["threshold_source"] = "val"
        metrics_path = run_dir / f"final_metrics_{split_name}.json"
        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    eval_and_save("val", val_ids, val_y_true, val_y_score)

    tm_ids, tm_y_true, tm_y_score_p1 = run_eval(test_main_loader)
    tm_y_score = _apply_score_transform(tm_y_score_p1, score_transform)
    eval_and_save("test_main", tm_ids, tm_y_true, tm_y_score)

    jbb_ids, jbb_y_true, jbb_y_score_p1 = run_eval(test_jbb_loader)
    jbb_y_score = _apply_score_transform(jbb_y_score_p1, score_transform)
    eval_and_save("test_jbb", jbb_ids, jbb_y_true, jbb_y_score)

    # Save adapter + tokenizer
    adapter_dir = run_dir / "lora_adapter"
    model.save_pretrained(adapter_dir)
    tokenizer.save_pretrained(adapter_dir)

    repo_root = Path(__file__).resolve().parents[1]
    git_commit = _get_git_commit(repo_root)
    manifest_path = Path(args.train).parent / "manifest.json"
    manifest_hash = _sha256_file(manifest_path) if manifest_path.exists() else None

    config = {
        "dataset_name": _infer_dataset_name(Path(args.train)),
        "detector": "lora",
        "unicode": use_unicode,
        "baseline_version": BASELINE_VERSION,
        "attack_class_index": attack_class_index,
        "attack_label": args.attack_label,
        "score_is_attack_prob": True,
        "score_transform": score_transform,
        "score_transform_source": "val",
        "val_threshold": float(op.threshold),
        "val_fpr_actual": float(op.fpr),
        "val_tpr_at_fpr": float(op.tpr),
        "splits": ["val", "test_main", "test_jbb"],
        "train_path": str(Path(args.train).resolve()),
        "val_path": str(Path(args.val).resolve()),
        "test_main_path": str(Path(args.test_main).resolve()),
        "test_jbb_path": str(Path(args.test_jbb).resolve()),
        "target_fpr": TARGET_FPR,
        "model_name": backbone,
        "backbone": backbone,
        "seed": args.seed,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir.resolve()),
        "max_length": args.max_length,
        "batch_size": args.batch_size,
        "grad_accum": args.grad_accum,
        "lr": args.lr,
        "epochs": args.epochs,
        "warmup_ratio": DEFAULT_WARMUP_RATIO,
        "total_steps": total_steps,
        "lora": {
            "r": LORA_R,
            "alpha": LORA_ALPHA,
            "dropout": LORA_DROPOUT,
            "target_modules": list(lora_config.target_modules or []),
            "modules_to_save": list(modules_to_save),
        },
        "device": device,
    }
    if git_commit:
        config["git_commit"] = git_commit
    if manifest_hash:
        config["dataset_manifest_path"] = str(manifest_path.resolve())
        config["dataset_manifest_sha256"] = manifest_hash
    (run_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    print(f"Wrote artifacts to {run_dir}")


if __name__ == "__main__":
    main()
