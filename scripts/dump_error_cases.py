from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


def _load_jsonl(path: Path) -> Iterable[Dict]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _shorten(text: str, limit: int = 180) -> str:
    cleaned = " ".join(text.replace("\n", " ").replace("\r", " ").split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3] + "..."


def _load_threshold(run_dir: Path) -> float:
    cfg_path = run_dir / "config.json"
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        threshold = cfg.get("val_threshold")
        if threshold is not None:
            return float(threshold)
    metrics_path = run_dir / "final_metrics_val.json"
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        threshold = metrics.get("val_threshold", metrics.get("threshold"))
        if threshold is not None:
            return float(threshold)
    raise RuntimeError("val_threshold not found in config.json or final_metrics_val.json")


def _load_text_lookup(path: Path, ids: set[str]) -> Dict[str, str]:
    lookup: Dict[str, str] = {}
    for row in _load_jsonl(path):
        row_id = row.get("id")
        if row_id in ids:
            lookup[row_id] = row.get("text", "")
            if len(lookup) == len(ids):
                break
    return lookup


def _select_errors(
    preds: List[Tuple[str, int, float]],
    threshold: float,
) -> Tuple[List[Tuple[str, int, float, str]], List[Tuple[str, int, float, str]]]:
    fps: List[Tuple[str, int, float, str]] = []
    fns: List[Tuple[str, int, float, str]] = []
    for ex_id, label, score in preds:
        decision = "attack" if score >= threshold else "safe"
        if label == 0 and decision == "attack":
            fps.append((ex_id, label, score, decision))
        elif label == 1 and decision == "safe":
            fns.append((ex_id, label, score, decision))
    fps_sorted = sorted(fps, key=lambda x: x[2], reverse=True)[:20]
    fns_sorted = sorted(fns, key=lambda x: x[2])[:20]
    return fps_sorted, fns_sorted


def _write_markdown(
    path: Path,
    title: str,
    threshold: float,
    rows: List[Tuple[str, int, float, str]],
    texts: Dict[str, str],
) -> None:
    lines = [f"# {title}", "", f"val_threshold: {threshold:.6f}", ""]
    lines.append("| rank | id | score | label | decision | text_snippet |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for idx, (ex_id, label, score, decision) in enumerate(rows, start=1):
        snippet = _shorten(texts.get(ex_id, ""))
        lines.append(f"| {idx} | {ex_id} | {score:.6f} | {label} | {decision} | {snippet} |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Dump top false positives/negatives for a split.")
    ap.add_argument("--run_dir", required=True, help="Path to run directory.")
    ap.add_argument("--split", required=True, help="Split name (e.g., test_main_unicode).")
    ap.add_argument("--out_fp", required=True, help="Output markdown for false positives.")
    ap.add_argument("--out_fn", required=True, help="Output markdown for false negatives.")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir)
    split = args.split
    pred_path = run_dir / f"predictions_{split}.jsonl"
    if not pred_path.exists():
        raise SystemExit(f"Missing predictions file: {pred_path}")

    cfg_path = run_dir / "config.json"
    if not cfg_path.exists():
        raise SystemExit(f"Missing config.json in {run_dir}")
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    data_key = f"{split}_path"
    data_path = cfg.get(data_key)
    if not data_path:
        raise SystemExit(f"Missing {data_key} in config.json")

    threshold = _load_threshold(run_dir)

    preds: List[Tuple[str, int, float]] = []
    for row in _load_jsonl(pred_path):
        preds.append((row["id"], int(row["label"]), float(row["score"])))

    fps, fns = _select_errors(preds, threshold)
    needed_ids = {ex_id for ex_id, _, _, _ in fps + fns}
    texts = _load_text_lookup(Path(data_path), needed_ids)

    _write_markdown(Path(args.out_fp), f"False Positives ({split})", threshold, fps, texts)
    _write_markdown(Path(args.out_fn), f"False Negatives ({split})", threshold, fns, texts)

    print(f"Wrote FP to {args.out_fp}")
    print(f"Wrote FN to {args.out_fn}")


if __name__ == "__main__":
    main()
