# Contributing

## Scope

This repository is a capstone project first and a reusable portfolio project second. Changes should improve reproducibility, demo reliability, or the clarity of the thesis-facing evidence pack.

## Development workflow

1. Create a local environment with `scripts/setup_dev.ps1` or `scripts/setup_dev.sh`.
2. Make small, reviewable changes with a clear problem statement.
3. Run the local quality gates before opening a pull request:

```bash
pytest -q
ruff check .
```

## Expectations for changes

- Keep the CLI contract stable unless the change intentionally updates the interface and the docs/tests are updated in the same commit.
- Treat `data/v1/spec.md` and `src/data/io.py` as the source of truth for dataset schema changes.
- Do not rewrite locked experiment artifacts under `reports/week7/locked_eval_pack/`.
- Avoid introducing secret-bearing `.env` flows unless the runtime actually needs them.

## Pull request checklist

- tests added or updated when behavior changes
- README or docs updated if user-facing commands or outputs changed
- thesis-facing claims kept aligned with `week7_norm_only`
- no generated demo outputs committed unless they are intentional reference artifacts
