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
- CLI smoke: `jbd --help` and `jbd predict --detector rules`

## Not covered yet

- LoRA inference (requires local weights)
- Batch CLI outputs on large files
- Performance profiling or GPU execution
