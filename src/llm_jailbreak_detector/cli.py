from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .io import iter_input_records, write_jsonl
from .normalize import normalize_text
from .predict import Predictor


def _parse_threshold(value: str | None) -> float | str | None:
    if value is None:
        return None
    if value.lower() == "val":
        return "val"
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError("threshold must be a float or 'val'") from exc


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jbd",
        description="Jailbreak detector CLI (rules offline, LoRA optional)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    predict = sub.add_parser("predict", help="Score a single text")
    predict.add_argument("--text", required=True, help="Input text")
    predict.add_argument(
        "--detector",
        choices=["rules", "lora"],
        default="rules",
        help="Detector backend (default: rules)",
    )
    predict.add_argument("--run_dir", help="Run directory for LoRA detector")
    predict.add_argument("--threshold", help="Float or 'val' (lora only)")
    predict.add_argument("--normalize", action="store_true", help="Normalize before scoring")
    predict.add_argument("--drop-mn", action="store_true", help="Drop Mn marks")
    predict.add_argument("--id", dest="record_id", help="Optional record id")

    batch = sub.add_parser("batch", help="Score a batch input (jsonl/txt)")
    batch.add_argument("--input", required=True, help="Input .jsonl or .txt")
    batch.add_argument("--output", required=True, help="Output .jsonl")
    batch.add_argument(
        "--detector",
        choices=["rules", "lora"],
        default="rules",
        help="Detector backend (default: rules)",
    )
    batch.add_argument("--run_dir", help="Run directory for LoRA detector")
    batch.add_argument("--threshold", help="Float or 'val' (lora only)")
    batch.add_argument("--normalize", action="store_true", help="Normalize before scoring")
    batch.add_argument("--drop-mn", action="store_true", help="Drop Mn marks")

    normalize = sub.add_parser("normalize", help="Normalize text only")
    normalize.add_argument("--text", required=True, help="Input text")
    normalize.add_argument("--drop-mn", action="store_true", help="Drop Mn marks")

    return parser


def _run_predict(args: argparse.Namespace) -> int:
    try:
        threshold = _parse_threshold(args.threshold)
        predictor = Predictor(detector=args.detector, run_dir=args.run_dir)
        result = predictor.predict(
            args.text,
            threshold=threshold,
            normalize_infer=args.normalize,
            drop_mn=args.drop_mn,
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        if args.detector == "lora":
            print("hint: Use --detector rules for offline mode.", file=sys.stderr)
        return 2

    payload = {
        "text": args.text,
        "score": result.score,
        "threshold": result.threshold,
        "flagged": bool(result.label),
        "detector": result.detector,
        "normalize_infer": bool(result.metadata.get("normalize_infer")),
    }
    if args.record_id is not None:
        payload["id"] = args.record_id
    print(json.dumps(payload, ensure_ascii=True))
    return 0


def _run_batch(args: argparse.Namespace) -> int:
    try:
        threshold = _parse_threshold(args.threshold)
        predictor = Predictor(detector=args.detector, run_dir=args.run_dir)
        rows = []
        for record in iter_input_records(Path(args.input)):
            text = record["text"]
            result = predictor.predict(
                text,
                threshold=threshold,
                normalize_infer=args.normalize,
                drop_mn=args.drop_mn,
            )
            payload = {
                "text": text,
                "score": result.score,
                "threshold": result.threshold,
                "flagged": bool(result.label),
                "detector": result.detector,
                "normalize_infer": bool(result.metadata.get("normalize_infer")),
            }
            if "id" in record:
                payload["id"] = record["id"]
            rows.append(payload)
        write_jsonl(Path(args.output), rows)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        if args.detector == "lora":
            print("hint: Use --detector rules for offline mode.", file=sys.stderr)
        return 2
    return 0


def _run_normalize(args: argparse.Namespace) -> int:
    output = normalize_text(args.text, drop_mn=args.drop_mn)
    print(output)
    return 0


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    if args.command == "predict":
        return _run_predict(args)
    if args.command == "batch":
        return _run_batch(args)
    if args.command == "normalize":
        return _run_normalize(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
