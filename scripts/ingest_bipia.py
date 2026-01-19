from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from typing import Dict, Iterable, Optional

import pandas as pd
import jsonlines

from dataset_utils import (
    format_text,
    make_group_id,
    make_id,
    sha256_str,
    write_jsonl,
)


def _pick_col(columns: Iterable[str], candidates: Iterable[str]) -> Optional[str]:
    cols = {c.lower(): c for c in columns}
    for cand in candidates:
        if cand.lower() in cols:
            return cols[cand.lower()]
    return None


def _ensure_bipia_repo(repo_dir: str, no_setup: bool) -> None:
    if os.path.isdir(repo_dir):
        return
    if no_setup:
        raise SystemExit(
            f"Missing {repo_dir}. Run without --no_setup to clone BIPIA."
        )
    os.makedirs(os.path.dirname(repo_dir), exist_ok=True)
    subprocess.check_call(
        ["git", "clone", "https://github.com/microsoft/BIPIA", repo_dir]
    )


def _infer_label(row: Dict, label_col: Optional[str]) -> int:
    if label_col:
        return int(row[label_col])
    attack_str = row.get("attack_str")
    if isinstance(attack_str, str) and attack_str.strip():
        return 1
    attack_name = row.get("attack_name")
    if isinstance(attack_name, str) and attack_name.strip():
        return 1
    for col in ("label", "is_attack", "is_malicious", "attack"):
        if col in row:
            return int(row[col])
    return 0


def _resolve_prompt(row: Dict, prompt_col: Optional[str]) -> str:
    if prompt_col:
        return str(row.get(prompt_col, ""))
    for col in ("user_query", "query", "prompt", "question", "user_prompt"):
        if col in row:
            return str(row.get(col, ""))
    raise ValueError("Could not infer prompt column. Use --prompt_col.")


def _resolve_context(row: Dict, context_col: Optional[str], attack_context_col: Optional[str], label: int) -> str:
    if label == 1 and attack_context_col:
        val = row.get(attack_context_col)
        if val is not None and str(val).strip():
            return str(val)
    if context_col:
        return str(row.get(context_col, ""))
    for col in ("context", "retrieved_context", "document", "doc", "passage", "context_text"):
        if col in row:
            return str(row.get(col, ""))
    return ""


def _resolve_context_doc_id(row: Dict) -> Optional[str]:
    for col in ("doc_id", "context_id", "document_id", "docid"):
        if col in row:
            val = row.get(col)
            if val is not None and str(val).strip():
                return str(val)
    return None


def _rows_to_examples(
    df: pd.DataFrame,
    task: str,
    split: str,
    prompt_col: Optional[str],
    context_col: Optional[str],
    attack_context_col: Optional[str],
    label_col: Optional[str],
) -> Iterable[Dict]:
    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        label = _infer_label(row_dict, label_col)
        prompt = _resolve_prompt(row_dict, prompt_col).strip()
        context = _resolve_context(row_dict, context_col, attack_context_col, label)
        if not prompt:
            continue
        text = format_text(prompt, context)

        context_doc_id = _resolve_context_doc_id(row_dict)
        if context_doc_id:
            group_payload = f"{task}|{context_doc_id}"
        else:
            group_payload = f"{task}|{sha256_str(context)}"
        group_id = make_group_id("bipia", group_payload)

        row_payload = f"{task}|{split}|{sha256_str(prompt)}|{sha256_str(context)}|{idx}"
        ex_id = make_id("bipia", row_payload)

        yield {
            "id": ex_id,
            "text": text,
            "label": label,
            "attack_type": "prompt_injection_indirect" if label == 1 else "benign",
            "source": "bipia",
            "group_id": group_id,
        }


def _clean_rows_from_contexts(context_path: str, task: str, split: str) -> Iterable[Dict]:
    rows = []
    with jsonlines.open(context_path, "r") as reader:
        for idx, row in enumerate(reader.iter()):
            row = dict(row)
            row["task_name"] = task
            row["split"] = split
            row["attack_name"] = ""
            row["attack_str"] = ""
            row["position"] = "clean"
            rows.append(row)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo_dir", default="external/BIPIA")
    ap.add_argument("--tasks", default="email,table")
    ap.add_argument("--seed", type=int, default=2023)
    ap.add_argument("--out_train", default="data/processed/bipia_train.jsonl")
    ap.add_argument("--out_test", default="data/processed/bipia_test.jsonl")
    ap.add_argument("--manifest", default="data/processed/bipia_manifest.json")
    ap.add_argument("--prompt_col")
    ap.add_argument("--context_col")
    ap.add_argument("--attack_context_col")
    ap.add_argument("--label_col")
    ap.add_argument("--print_columns", action="store_true")
    ap.add_argument("--no_clean", action="store_true")
    ap.add_argument("--no_setup", action="store_true")
    args = ap.parse_args()

    _ensure_bipia_repo(args.repo_dir, args.no_setup)
    sys.path.insert(0, args.repo_dir)

    try:
        from bipia.data import AutoPIABuilder
    except ModuleNotFoundError as e:
        missing = getattr(e, "name", None) or str(e)
        raise SystemExit(
            f"Missing dependency while importing BIPIA: {missing}. "
            "Install it in your active venv, then rerun."
        ) from e
    except Exception as e:
        raise SystemExit(
            f"Failed to import BIPIA from local repo: {type(e).__name__}: {e}"
        ) from e

    tasks = [t.strip() for t in args.tasks.split(",") if t.strip()]
    manifest = defaultdict(Counter)
    train_rows = []
    test_rows = []

    for task in tasks:
        builder = AutoPIABuilder.from_name(task)(seed=args.seed)
        for split in ("train", "test"):
            context_data_file = os.path.join(args.repo_dir, "benchmark", task, f"{split}.jsonl")
            attack_data_file = os.path.join(args.repo_dir, "benchmark", f"text_attack_{split}.json")
            df = builder(context_data_file, attack_data_file, enable_stealth=False)
            if args.print_columns:
                print(f"{task}/{split} columns: {list(df.columns)}")
            examples = []
            examples.extend(
                _rows_to_examples(
                    df=df,
                    task=task,
                    split=split,
                    prompt_col=args.prompt_col,
                    context_col=args.context_col,
                    attack_context_col=args.attack_context_col,
                    label_col=args.label_col,
                )
            )
            if not args.no_clean:
                clean_df = pd.DataFrame(
                    _clean_rows_from_contexts(context_data_file, task, split)
                )
                examples.extend(
                    _rows_to_examples(
                        df=clean_df,
                        task=task,
                        split=split,
                        prompt_col=args.prompt_col,
                        context_col=args.context_col,
                        attack_context_col=None,
                        label_col=args.label_col,
                    )
                )
            for ex in examples:
                manifest[task][str(ex["label"])] += 1
            if split == "train":
                train_rows.extend(examples)
            else:
                test_rows.extend(examples)

    write_jsonl(args.out_train, train_rows)
    write_jsonl(args.out_test, test_rows)
    with open(args.manifest, "w", encoding="utf-8") as f:
        json.dump({k: dict(v) for k, v in manifest.items()}, f, indent=2)

    print(f"Wrote: {args.out_train} ({len(train_rows)})")
    print(f"Wrote: {args.out_test} ({len(test_rows)})")
    print(f"Wrote: {args.manifest}")


if __name__ == "__main__":
    main()
