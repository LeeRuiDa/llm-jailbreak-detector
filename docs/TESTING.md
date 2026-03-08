# Testing

## Run tests

```bash
pytest -q
```

If you want the CLI smoke tests to exercise the `jbd` entrypoint, install the package first:

```bash
pip install -e .
```

## Coverage

- Normalization behavior (NFKC + Cf/Mn stripping)
- Rules detector predictions
- CLI smoke coverage for:
  - `jbd --help`
  - `jbd doctor`
  - `jbd predict --detector rules`
  - `jbd batch --detector rules`
  - invalid JSONL failure path
  - missing `--run_dir` failure path for LoRA

## Not covered yet

- LoRA inference (requires local weights)
- Performance profiling or GPU execution
- End-to-end reproduction of Week 7 training runs in CI
