from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple


def _load_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _format_val(val: object) -> str:
    if val is None:
        return "-"
    if isinstance(val, float):
        return f"{val:.4f}"
    return str(val)


def _infer_split(metrics_path: Path, cfg: Dict) -> str:
    stem = metrics_path.stem
    if stem.startswith("final_metrics_"):
        return stem[len("final_metrics_") :]
    return str(cfg.get("split", "-"))


def _infer_dataset(cfg: Dict) -> str:
    for key in ("dataset_name", "data", "dataset", "eval_data"):
        val = cfg.get(key)
        if isinstance(val, str) and val:
            return val
    return "-"


def _infer_detector(cfg: Dict) -> str:
    for key in ("detector", "model_type", "model_name"):
        val = cfg.get(key)
        if isinstance(val, str) and val:
            return val
    return "-"


def _infer_backbone(cfg: Dict) -> str:
    for key in ("backbone", "model_name"):
        val = cfg.get(key)
        if isinstance(val, str) and val:
            return val
    return "-"


def _infer_unicode(cfg: Dict) -> str:
    for key in ("unicode", "use_unicode_preprocess", "use_unicode"):
        if key in cfg:
            return str(cfg.get(key))
    return "-"


def _dataset_tag(dataset: str, clean_tag: str, adv_tag: str) -> str:
    lowered = dataset.lower()
    if adv_tag.lower() in lowered:
        return "unicode_adv"
    if clean_tag.lower() in lowered:
        return "clean"
    return "other"


def _parse_timestamp(cfg: Dict, metrics_path: Path) -> Tuple[float, str]:
    raw = cfg.get("timestamp")
    if isinstance(raw, str) and raw:
        try:
            ts = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            return ts.timestamp(), raw
        except ValueError:
            pass
    mtime = metrics_path.stat().st_mtime
    return mtime, f"mtime:{datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs_dir", default="runs")
    ap.add_argument("--clean_tag", default="v1")
    ap.add_argument("--adv_tag", default="v1_adv")
    ap.add_argument("--splits", default="")
    args = ap.parse_args()

    split_filter = {s.strip() for s in args.splits.split(",") if s.strip()}

    runs_dir = Path(args.runs_dir)
    metrics_paths = sorted(runs_dir.rglob("final_metrics*.json"))
    if not metrics_paths:
        raise SystemExit(f"No final_metrics files found under {runs_dir}")

    rows: List[List[str]] = []
    chosen: Dict[Tuple[str, str, str, str], Tuple[float, Path, List[str]]] = {}
    collisions: Dict[Tuple[str, str, str, str], int] = {}
    for metrics_path in metrics_paths:
        cfg_path = metrics_path.parent / "config.json"
        if not cfg_path.exists():
            continue
        cfg = _load_json(cfg_path)
        metrics = _load_json(metrics_path)

        dataset = _infer_dataset(cfg)
        tag = _dataset_tag(dataset, args.clean_tag, args.adv_tag)
        if tag == "other":
            continue
        split = _infer_split(metrics_path, cfg)
        if split_filter and split not in split_filter:
            continue

        row = [
            _infer_detector(cfg),
            _infer_backbone(cfg),
            _infer_unicode(cfg),
            tag,
            split,
            _format_val(metrics.get("auroc")),
            _format_val(metrics.get("tpr_at_fpr")),
            _format_val(metrics.get("asr_at_threshold")),
        ]
        key = (row[0], row[1], row[2], row[3], row[4])
        ts, _ = _parse_timestamp(cfg, metrics_path)
        if key in chosen:
            collisions[key] = collisions.get(key, 1) + 1
            if ts > chosen[key][0]:
                chosen[key] = (ts, metrics_path, row)
        else:
            chosen[key] = (ts, metrics_path, row)

    rows = [entry[2] for entry in chosen.values()]

    headers = [
        "detector",
        "backbone",
        "unicode",
        "dataset",
        "split",
        "auroc",
        "tpr@1%fpr",
        "asr",
    ]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in sorted(rows):
        lines.append("| " + " | ".join(row) + " |")
    if collisions:
        for key, count in sorted(collisions.items()):
            detector, backbone, unicode_flag, dataset_tag, split = key
            print(
                "Dedup: picked latest of "
                f"{count} for {detector}/{backbone}/{unicode_flag}/{dataset_tag}/{split}"
            )
    print("\n".join(lines))


if __name__ == "__main__":
    main()
