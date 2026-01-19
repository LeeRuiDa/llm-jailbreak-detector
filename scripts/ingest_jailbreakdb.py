from __future__ import annotations

import argparse
import json
import os
import random
import sys
from collections import Counter
from typing import Dict, Iterable, List, Optional

from dataset_utils import format_text, sha256_str, write_jsonl

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.preprocess.unicode import normalize_text

try:
    import datasets
    import fsspec
    import huggingface_hub
    from datasets import load_dataset
    from huggingface_hub import HfApi
except ImportError as e:
    raise SystemExit(
        "Missing dependency: datasets/huggingface_hub/fsspec. "
        "Install with `pip install datasets huggingface_hub fsspec`."
    ) from e


EMPTY_REPO_FILES = {".gitattributes", "README.md"}
DATA_EXTS = (".csv", ".parquet", ".jsonl", ".json")


def _print_versions() -> None:
    print(
        f"datasets {datasets.__version__} "
        f"huggingface_hub {huggingface_hub.__version__}"
    )


def _list_repo_files(repo_id: str) -> List[str]:
    api = HfApi()
    files = api.list_repo_files(repo_id, repo_type="dataset")
    print("Repo files:")
    for path in files:
        print(f"- {path}")
    return files


def _ensure_repo_has_data(repo_id: str, files: List[str]) -> None:
    if set(files) <= EMPTY_REPO_FILES:
        raise SystemExit(
            f"Repo {repo_id} has no data files (only README/.gitattributes). "
            "Known empty example: haorandai/JailbreakDB. "
            "Check the repo_id or dataset access."
        )


def _pick_data_files(files: List[str]) -> List[str]:
    candidates = [f for f in files if f.lower().endswith(DATA_EXTS)]
    return candidates


def _try_load_streaming(
    repo_id: str, files: List[str]
) -> Iterable[Dict]:
    config_names: List[str] = []
    try:
        config_names = datasets.get_dataset_config_names(repo_id)
    except Exception:
        config_names = []

    if config_names:
        config = config_names[0]
        print(f"Using config: {config}")
    else:
        config = None

    try:
        if config:
            ds = load_dataset(repo_id, config, split="train", streaming=True)
        else:
            ds = load_dataset(repo_id, split="train", streaming=True)
        print("Using split: train")
        return ds
    except Exception:
        pass

    data_files = _pick_data_files(files)
    if not data_files:
        raise SystemExit(
            f"No CSV/Parquet/JSONL/JSON files found in {repo_id}. "
            "Check the repo_id or dataset access."
        )

    preferred_ext = None
    if any(f.endswith(".parquet") for f in data_files):
        preferred_ext = ".parquet"
    elif any(f.endswith(".csv") for f in data_files):
        preferred_ext = ".csv"
    elif any(f.endswith(".jsonl") for f in data_files):
        preferred_ext = ".jsonl"
    elif any(f.endswith(".json") for f in data_files):
        preferred_ext = ".json"
    if preferred_ext:
        data_files = [f for f in data_files if f.endswith(preferred_ext)]

    print("Using data_files:")
    for path in data_files:
        print(f"- {path}")

    if preferred_ext == ".parquet":
        file_format = "parquet"
    elif preferred_ext in (".json", ".jsonl"):
        file_format = "json"
    else:
        file_format = "csv"
    ds = load_dataset(
        file_format, data_files={"train": data_files}, split="train", streaming=True
    )
    print("Using split: train")
    return ds


def _coerce_label(val: object) -> int:
    if val is None:
        return 0
    if isinstance(val, bool):
        return int(val)
    if isinstance(val, (int, float)):
        return 1 if int(val) == 1 else 0
    text = str(val).strip().lower()
    if text in {"1", "true", "yes", "y", "jailbreak", "attack"}:
        return 1
    return 0


def _pick_attack_type(row: Dict, label: int) -> str:
    if label == 0:
        return "benign"
    for key in ("tactic", "category", "attack_type"):
        val = row.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return "jailbreak"


def _pick_source(row: Dict) -> str:
    src = row.get("source") or row.get("dataset") or row.get("origin")
    if isinstance(src, str) and src.strip():
        return f"jailbreakdb:{src.strip()}"
    return "jailbreakdb"


def _row_to_example(row: Dict) -> Optional[Dict]:
    prompt = row.get("user_prompt") or row.get("prompt") or row.get("instruction")
    context = row.get("system_prompt") or row.get("context") or ""
    if not prompt:
        return None
    text = format_text(str(prompt), str(context))
    normalized = normalize_text(text)
    group_id = sha256_str(normalized)
    ex_id = f"jailbreakdb:{group_id[:16]}"
    label = _coerce_label(row.get("jailbreak", row.get("label")))
    attack_type = _pick_attack_type(row, label)
    source = _pick_source(row)
    return {
        "id": ex_id,
        "text": text,
        "label": label,
        "attack_type": attack_type,
        "source": source,
        "group_id": group_id,
    }


def _reservoir_sample(
    rows: Iterable[Dict],
    sample_k: int,
    seed: int,
) -> List[Dict]:
    rng = random.Random(seed)
    reservoirs = {0: [], 1: []}
    seen = {0: 0, 1: 0}

    for row in rows:
        label = row["label"]
        seen[label] += 1
        bucket = reservoirs[label]
        if len(bucket) < sample_k:
            bucket.append(row)
        else:
            idx = rng.randint(0, seen[label] - 1)
            if idx < sample_k:
                bucket[idx] = row

    combined = reservoirs[0] + reservoirs[1]
    rng.shuffle(combined)
    return combined


def _count_stats(rows: Iterable[Dict]) -> Dict[str, Dict[str, int]]:
    label_counts = Counter()
    attack_counts = Counter()
    for row in rows:
        label_counts[str(row["label"])] += 1
        attack_counts[str(row["attack_type"])] += 1
    return {
        "label_counts": dict(label_counts),
        "attack_type_counts": dict(attack_counts),
    }


def main() -> None:
    _print_versions()
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo_id", default="youbin2014/JailbreakDB")
    ap.add_argument("--out_jsonl", default="data/processed/jailbreakdb.jsonl")
    ap.add_argument("--sample_k", type=int)
    ap.add_argument("--seed", type=int, default=2023)
    ap.add_argument("--no_validate", action="store_true")
    args = ap.parse_args()

    files = _list_repo_files(args.repo_id)
    _ensure_repo_has_data(args.repo_id, files)

    dataset = _try_load_streaming(args.repo_id, files)
    rows = (ex for ex in ( _row_to_example(r) for r in dataset) if ex)

    if args.sample_k:
        sampled = _reservoir_sample(rows, args.sample_k, args.seed)
        write_jsonl(args.out_jsonl, sampled)
        stats = _count_stats(sampled)
    else:
        counts = Counter()
        attack_counts = Counter()
        with open(args.out_jsonl, "w", encoding="utf-8") as f:
            for ex in rows:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
                counts[str(ex["label"])] += 1
                attack_counts[str(ex["attack_type"])] += 1
        stats = {
            "label_counts": dict(counts),
            "attack_type_counts": dict(attack_counts),
        }

    print(json.dumps(stats, indent=2))
    print(f"Wrote: {args.out_jsonl}")

    if not args.no_validate:
        try:
            from src.data.io import load_examples
        except Exception as e:
            raise SystemExit(f"Failed to import loader for validation: {e}") from e
        examples = load_examples(args.out_jsonl)
        validation_counts = Counter()
        attack_counts = Counter()
        for ex in examples:
            validation_counts[str(ex.label)] += 1
            attack_counts[str(ex.attack_type)] += 1
        print(
            json.dumps(
                {
                    "validated_label_counts": dict(validation_counts),
                    "validated_attack_type_counts": dict(attack_counts),
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
