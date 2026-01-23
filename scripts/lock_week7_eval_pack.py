from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List


REPO_ROOT = Path(__file__).resolve().parents[1]
SPLITS = [
    "val",
    "test_main",
    "test_jbb",
    "test_main_unicode",
    "test_jbb_unicode",
    "test_main_adv2",
    "test_jbb_adv2",
    "test_main_rewrite",
    "test_jbb_rewrite",
]

TABLE_FILES = [
    "week7_table_A_clean_unicode.md",
    "week7_table_B_adv2_rewrite.md",
    "week7_table_C_threshold_transfer.md",
    "week7_table_D_ablation_effects.md",
    "week7_metrics_long.md",
    "week7_metrics_long.csv",
]

PLOT_SPLITS = [
    "test_main_adv2",
    "test_jbb_adv2",
]

ERROR_CASE_FILES = [
    "test_main_adv2_fp.md",
    "test_main_adv2_fn.md",
    "test_jbb_adv2_fp.md",
    "test_jbb_adv2_fn.md",
    "test_main_rewrite_fp.md",
    "test_main_rewrite_fn.md",
    "test_jbb_rewrite_fp.md",
    "test_jbb_rewrite_fn.md",
]


def _get_git_commit() -> str | None:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True)
            .strip()
        )
    except Exception:
        return None


def _get_pip_freeze() -> List[str]:
    try:
        output = subprocess.check_output(
            [sys.executable, "-m", "pip", "freeze"], text=True, stderr=subprocess.DEVNULL
        )
        return [line.strip() for line in output.splitlines() if line.strip()]
    except Exception:
        return []


def _get_python_version() -> str:
    try:
        output = subprocess.check_output(
            [sys.executable, "--version"], text=True, stderr=subprocess.STDOUT
        )
        return output.strip()
    except Exception:
        return sys.version.replace("\n", " ")


def _get_gpu_info() -> str:
    try:
        import torch

        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            version = torch.version.cuda or "unknown"
            count = torch.cuda.device_count()
            return f"cuda={version} devices={count} name={name}"
        return "none"
    except Exception:
        return "unknown"


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        print(f"Warning: missing directory {src}")
        return
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _load_config(run_dir: Path) -> dict:
    cfg_path = run_dir / "config.json"
    if not cfg_path.exists():
        raise FileNotFoundError(f"Missing config.json in {run_dir}")
    return json.loads(cfg_path.read_text(encoding="utf-8"))


def _write_env(path: Path) -> None:
    git_commit = _get_git_commit() or "unknown"
    python_version = _get_python_version()
    pip_freeze = _get_pip_freeze()
    gpu_info = _get_gpu_info()

    lines = [
        f"git_commit: {git_commit}",
        f"python: {python_version}",
        f"gpu: {gpu_info}",
        "pip_freeze:",
    ]
    for line in pip_freeze:
        lines.append(f"  {line}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_week7_final(path: Path, run_id: str, cfg: dict, decision_commit: str, rationale: str) -> None:
    lines = [
        "# Week 7 Final (Ablations)",
        "",
        f"winner_run_id: {run_id}",
        "",
        "factors:",
        f"- normalize_train: {bool(cfg.get('normalize_train'))}".lower(),
        f"- aug_adv2_prob: {cfg.get('aug_adv2_prob')}",
        f"- aug_rewrite_prob: {cfg.get('aug_rewrite_prob')}",
        f"- aug_seed: {cfg.get('aug_seed')}",
        "",
        "eval_protocol:",
        "- script: scripts/eval_week7_grid.py",
        f"- splits: {', '.join(SPLITS)}",
        "- normalize_infer: off",
        "- threshold: val_threshold from config.json",
        "",
        f"decision_commit: {decision_commit}",
        "",
        "rationale:",
        rationale.strip() or "TBD",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Lock Week 7 eval pack for a final run.")
    ap.add_argument("--run_id", required=True, help="Run directory name (e.g., lora_v1_deberta_normtrain)")
    ap.add_argument("--runs_root", default=str(REPO_ROOT / "runs"))
    ap.add_argument("--out_root", default=str(REPO_ROOT / "reports" / "week7" / "locked_eval_pack"))
    ap.add_argument("--tables_dir", default=str(REPO_ROOT / "reports" / "week7" / "results"))
    ap.add_argument("--figures_root", default=str(REPO_ROOT / "reports" / "week7" / "figures"))
    ap.add_argument("--errors_root", default=str(REPO_ROOT / "reports" / "week7" / "error_cases"))
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing locked pack")
    ap.add_argument("--rationale", default="TBD", help="Decision rationale text")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    run_id = args.run_id
    run_dir = Path(args.runs_root) / run_id
    if not run_dir.exists():
        raise FileNotFoundError(f"Run dir not found: {run_dir}")

    pack_dir = Path(args.out_root) / run_id
    if pack_dir.exists():
        if not args.overwrite:
            raise SystemExit(f"Locked eval pack already exists: {pack_dir}")
        shutil.rmtree(pack_dir)

    pack_dir.mkdir(parents=True, exist_ok=True)

    tables_dir = Path(args.tables_dir)
    tables_out = pack_dir / "tables"
    for name in TABLE_FILES:
        src = tables_dir / name
        if not src.exists():
            raise FileNotFoundError(f"Missing table: {src}")
        _copy_file(src, tables_out / name)

    metrics_md = Path(REPO_ROOT / "reports" / "week7" / f"{run_id}_metrics.md")
    if metrics_md.exists():
        _copy_file(metrics_md, pack_dir / metrics_md.name)

    figures_src = Path(args.figures_root) / run_id
    figures_out = pack_dir / "figures"
    for split in PLOT_SPLITS:
        for prefix in ("roc", "hist"):
            filename = f"{prefix}_{run_id}_{split}.png"
            src = figures_src / filename
            if not src.exists():
                raise FileNotFoundError(f"Missing plot: {src}")
            _copy_file(src, figures_out / filename)

    errors_src = Path(args.errors_root) / run_id
    errors_out = pack_dir / "error_cases"
    for name in ERROR_CASE_FILES:
        src = errors_src / name
        if not src.exists():
            raise FileNotFoundError(f"Missing error case file: {src}")
        _copy_file(src, errors_out / name)

    _write_env(pack_dir / "ENV.txt")

    cfg = _load_config(run_dir)
    decision_commit = cfg.get("git_commit") or _get_git_commit() or "unknown"
    final_md = REPO_ROOT / "reports" / "week7" / "WEEK7_FINAL.md"
    _write_week7_final(final_md, run_id, cfg, decision_commit, args.rationale)
    _copy_file(final_md, pack_dir / "WEEK7_FINAL.md")

    print(f"Locked eval pack created at {pack_dir}")


if __name__ == "__main__":
    main()
