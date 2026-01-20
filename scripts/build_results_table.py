from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


def _find_metrics_files(runs_dir: Path, names: List[str]) -> List[Path]:
    paths: List[Path] = []
    for name in names:
        paths.extend(runs_dir.rglob(name))
    return sorted(set(paths))


def _load_json(path: Path) -> Dict | List:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _format_val(val: object) -> str:
    if val is None:
        return "-"
    if isinstance(val, float):
        return f"{val:.4f}"
    return str(val)


def _resolve_run_id(runs_dir: Path, metrics_path: Path) -> str:
    try:
        return str(metrics_path.parent.relative_to(runs_dir))
    except ValueError:
        return str(metrics_path.parent)


def _load_config(metrics_path: Path) -> Dict:
    cfg_path = metrics_path.parent / "config.json"
    if cfg_path.exists():
        return _load_json(cfg_path)
    return {}


def _infer_dataset_for_split(cfg: Dict, split: str) -> str:
    if split and split != "-":
        split_key = f"{split}_path"
        val = cfg.get(split_key)
        if isinstance(val, str) and val:
            return val
    for key in ("dataset_name", "data", "dataset", "eval_data"):
        val = cfg.get(key)
        if isinstance(val, str) and val:
            return val
    return "-"


def _infer_unicode(cfg: Dict) -> str:
    for key in ("unicode", "use_unicode_preprocess", "use_unicode"):
        if key in cfg:
            return str(cfg.get(key))
    return "-"


def _infer_detector(cfg: Dict) -> str:
    for key in ("detector", "model_type", "model_name"):
        val = cfg.get(key)
        if isinstance(val, str) and val:
            return val
    return "-"


def _infer_backbone(cfg: Dict) -> str:
    detector = cfg.get("detector")
    if isinstance(detector, str) and detector.startswith("rules"):
        return "rules"
    for key in ("backbone", "model_name"):
        val = cfg.get(key)
        if isinstance(val, str) and val:
            return val
    return "-"


def _infer_split_from_filename(metrics_path: Path) -> str:
    stem = metrics_path.stem
    if stem.startswith("final_metrics_"):
        return stem[len("final_metrics_") :]
    for name in ("test_main_unicode", "test_jbb_unicode", "test_main", "test_jbb", "val", "train", "test"):
        if name in stem:
            return name
    return "-"


def _infer_split(cfg: Dict, metrics_path: Path) -> str:
    for key in ("split", "eval_split", "dataset_split"):
        val = cfg.get(key)
        if isinstance(val, str) and val:
            return val
    if metrics_path.name == "metrics.json":
        splits = cfg.get("splits")
        if isinstance(splits, list) and "val" in splits:
            return "val"
    split = _infer_split_from_filename(metrics_path)
    if split != "-":
        return split
    dataset = _infer_dataset_for_split(cfg, "")
    lowered = dataset.lower()
    for name in ("test_main_unicode", "test_jbb_unicode", "test_main", "test_jbb", "val", "train", "test"):
        if name in lowered:
            return name
    return "-"


def _pick_metrics(metrics: Dict | List) -> Dict:
    if isinstance(metrics, list):
        if not metrics:
            return {}
        return metrics[-1]
    return metrics


def _build_row(
    runs_dir: Path, metrics_path: Path, metrics: Dict | List, cfg: Dict
) -> List[str]:
    metrics_dict = _pick_metrics(metrics)
    run_id = _resolve_run_id(runs_dir, metrics_path)
    split = _infer_split(cfg, metrics_path)
    dataset = _infer_dataset_for_split(cfg, split)
    detector = _infer_detector(cfg)
    backbone = _infer_backbone(cfg)
    baseline_version = cfg.get("baseline_version", "-")
    git_commit = cfg.get("git_commit", "-")
    unicode_flag = _infer_unicode(cfg)
    return [
        run_id,
        split,
        dataset,
        detector,
        backbone,
        str(baseline_version) if baseline_version is not None else "-",
        str(git_commit) if git_commit is not None else "-",
        unicode_flag,
        _format_val(metrics_dict.get("auroc")),
        _format_val(metrics_dict.get("auprc")),
        _format_val(metrics_dict.get("tpr_at_fpr")),
        _format_val(metrics_dict.get("val_threshold", metrics_dict.get("threshold"))),
        _format_val(metrics_dict.get("fpr_at_val_threshold", metrics_dict.get("fpr_actual"))),
        _format_val(metrics_dict.get("tpr_at_val_threshold", metrics_dict.get("tpr_at_fpr"))),
        _format_val(metrics_dict.get("asr_at_threshold")),
    ]


def _warn_missing_config(run_id: str, cfg: Dict, warned: set[str]) -> None:
    missing = []
    for key in ("dataset_name", "detector", "unicode"):
        if key not in cfg:
            missing.append(key)
    if "split" not in cfg and "splits" not in cfg:
        missing.append("split")
    if missing and run_id not in warned:
        print(f"Warning: {run_id} missing config keys: {', '.join(missing)}")
        warned.add(run_id)


def _is_inf(value: object) -> bool:
    if isinstance(value, (int, float)):
        return value == float("inf") or value == float("-inf")
    return False


def _write_table(out_path: Path, headers: List[str], rows: List[List[str]]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs_dir", default="runs")
    ap.add_argument("--out", default="runs/results_table.md")
    ap.add_argument(
        "--require_config",
        action="store_true",
        help="Skip runs missing dataset_name/detector/unicode/split in config.json.",
    )
    ap.add_argument(
        "--metrics_names",
        default="final_metrics_val.json,final_metrics_test_main.json,final_metrics_test_jbb.json,final_metrics_test_main_unicode.json,final_metrics_test_jbb_unicode.json,final_metrics_test_main_adv2.json,final_metrics_test_jbb_adv2.json,final_metrics.json,metrics.json",
        help="Comma-separated metrics filenames to include.",
    )
    ap.add_argument(
        "--include_dataset",
        default="",
        help="Only include rows whose dataset field contains this substring.",
    )
    ap.add_argument(
        "--exclude_contains",
        default="data/sample",
        help="Exclude rows whose dataset field contains this substring (default: data/sample).",
    )
    args = ap.parse_args()

    runs_dir = Path(args.runs_dir)
    names = [n.strip() for n in args.metrics_names.split(",") if n.strip()]
    metrics_paths = _find_metrics_files(runs_dir, names)
    if not metrics_paths:
        raise SystemExit(f"No metrics files found under {runs_dir}.")

    rows: List[List[str]] = []
    seen: Dict[Tuple[str, str], Path] = {}
    warned: set[str] = set()
    for metrics_path in metrics_paths:
        metrics = _load_json(metrics_path)
        cfg = _load_config(metrics_path)
        run_id = _resolve_run_id(runs_dir, metrics_path)
        split = _infer_split(cfg, metrics_path)
        _warn_missing_config(run_id, cfg, warned)
        metrics_dict = _pick_metrics(metrics)
        val_threshold = metrics_dict.get("val_threshold", metrics_dict.get("threshold"))
        if _is_inf(val_threshold):
            continue

        dataset = _infer_dataset_for_split(cfg, split)
        detector = _infer_detector(cfg)
        backbone = _infer_backbone(cfg)
        unicode_flag = _infer_unicode(cfg)
        if args.require_config:
            missing_required = (
                split == "-"
                or dataset == "-"
                or detector == "-"
                or backbone == "-"
                or unicode_flag == "-"
            )
            if missing_required:
                continue
        if args.exclude_contains:
            excluded = args.exclude_contains.lower().replace("\\", "/")
            dataset_norm = str(dataset).lower().replace("\\", "/")
            if excluded in dataset_norm:
                continue
        if args.include_dataset and args.include_dataset not in dataset:
            continue
        key = (run_id, split)
        if key in seen:
            # Prefer final_metrics.json when both exist for the same run/split.
            if metrics_path.name.startswith("final_metrics"):
                seen[key] = metrics_path
            else:
                continue
        else:
            seen[key] = metrics_path

    for metrics_path in sorted(seen.values()):
        metrics = _load_json(metrics_path)
        cfg = _load_config(metrics_path)
        rows.append(_build_row(runs_dir, metrics_path, metrics, cfg))

    headers = [
        "run",
        "split",
        "dataset",
        "detector",
        "backbone",
        "baseline_version",
        "git_commit",
        "unicode",
        "auroc",
        "auprc",
        "tpr_at_fpr",
        "val_threshold",
        "fpr_at_val_threshold",
        "tpr_at_val_threshold",
        "asr_at_threshold",
    ]
    _write_table(Path(args.out), headers, rows)
    print(f"Wrote: {args.out}")


if __name__ == "__main__":
    main()
