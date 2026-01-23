from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC = REPO_ROOT / "reports" / "week7" / "week7_ablation_spec.json"
REQUIRED_RUN_KEYS = {"run_id", "normalize_train", "aug_adv2_prob", "aug_rewrite_prob", "aug_seed"}
REQUIRED_CONFIG_KEYS = {"normalize_train", "aug_adv2_prob", "aug_seed", "val_threshold"}


def _get_git_commit() -> str | None:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True)
            .strip()
        )
    except Exception:
        return None


def _load_spec(path: Path) -> Dict:
    if not path.exists():
        raise FileNotFoundError(f"Spec not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _require_keys(obj: Dict, keys: set[str], context: str) -> None:
    missing = sorted(k for k in keys if k not in obj)
    if missing:
        raise KeyError(f"Missing keys in {context}: {', '.join(missing)}")


def _resolve_run_dir(run_id: str) -> Path:
    run_path = Path(run_id)
    if run_path.is_absolute():
        return run_path
    if len(run_path.parts) > 1:
        return REPO_ROOT / run_path
    return REPO_ROOT / "runs" / run_path


def _resolve_data_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def _build_train_command(spec: Dict, run: Dict) -> tuple[List[str], Path]:
    dataset = spec.get("dataset") or {}
    _require_keys(dataset, {"train", "val", "test_main", "test_jbb"}, "spec.dataset")

    training = spec.get("training") or {}
    backbone = spec.get("backbone", "microsoft/deberta-v3-base")

    run_id = str(run["run_id"]).strip()
    if not run_id:
        raise ValueError("run_id must be a non-empty string")

    run_dir = _resolve_run_dir(run_id)

    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "train_lora.py"),
        "--train",
        str(_resolve_data_path(dataset["train"])),
        "--val",
        str(_resolve_data_path(dataset["val"])),
        "--test_main",
        str(_resolve_data_path(dataset["test_main"])),
        "--test_jbb",
        str(_resolve_data_path(dataset["test_jbb"])),
        "--backbone",
        backbone,
        "--epochs",
        str(training.get("epochs", 3)),
        "--batch_size",
        str(training.get("batch_size", 16)),
        "--lr",
        str(training.get("lr", 2e-4)),
        "--grad_accum",
        str(training.get("grad_accum", 2)),
        "--seed",
        str(training.get("seed", 42)),
        "--max_length",
        str(training.get("max_length", 256)),
        "--num_workers",
        str(training.get("num_workers", 0)),
        "--aug_adv2_prob",
        str(run["aug_adv2_prob"]),
        "--aug_rewrite_prob",
        str(run["aug_rewrite_prob"]),
        "--aug_seed",
        str(run["aug_seed"]),
        "--out_dir",
        str(run_dir),
    ]

    if training.get("unicode_preprocess"):
        cmd.append("--unicode_preprocess")
    if training.get("normalize_drop_mn"):
        cmd.append("--normalize_drop_mn")
    if run.get("normalize_train"):
        cmd.append("--normalize_train")

    return cmd, run_dir


def _validate_config(run_dir: Path) -> Dict:
    cfg_path = run_dir / "config.json"
    if not cfg_path.exists():
        raise FileNotFoundError(f"Missing config.json in {run_dir}")
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    missing = sorted(k for k in REQUIRED_CONFIG_KEYS if k not in cfg)
    if missing:
        raise KeyError(f"Missing keys in {cfg_path}: {', '.join(missing)}")
    if cfg.get("val_threshold") is None:
        raise RuntimeError(f"val_threshold missing in {cfg_path}")
    return cfg


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run Week 7 ablation training from spec.")
    ap.add_argument("--spec", default=str(DEFAULT_SPEC), help="Path to week7_ablation_spec.json")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    spec = _load_spec(Path(args.spec))

    runs = spec.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError("Spec must include a non-empty 'runs' list")

    if len(runs) != 4:
        raise ValueError(f"Expected exactly 4 runs in spec, found {len(runs)}")

    manifest: List[Dict] = []
    git_commit = _get_git_commit()

    for run in runs:
        if not isinstance(run, dict):
            raise TypeError("Each run entry must be an object")
        _require_keys(run, REQUIRED_RUN_KEYS, f"run {run.get('name', '<unnamed>')}")

        cmd, run_dir = _build_train_command(spec, run)
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, check=True)

        cfg = _validate_config(run_dir)

        manifest.append(
            {
                "run_id": run_dir.name,
                "run_dir": str(run_dir),
                "name": run.get("name"),
                "normalize_train": bool(run.get("normalize_train")),
                "aug_adv2_prob": float(run.get("aug_adv2_prob")),
                "aug_rewrite_prob": float(run.get("aug_rewrite_prob")),
                "aug_seed": int(run.get("aug_seed")),
                "seed": int(spec.get("training", {}).get("seed", 42)),
                "val_threshold": float(cfg.get("val_threshold")),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "git_commit": git_commit,
            }
        )

    out_path = REPO_ROOT / "reports" / "week7" / "run_manifest.json"
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote manifest: {out_path}")


if __name__ == "__main__":
    main()
