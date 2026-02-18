# Chapter 6 Reviewer Q&A

## Q1) Paste/produce Ch6.1-Ch6.5 text
- Full Chapter 6 manuscript is provided in:
  - `thesis/06_system_demo.md`
  - `ch6_system_demo_revised.md`
- Sections included: `6.1` Overview & deployment context, `6.2` architecture + Figure 6.1, `6.3` implementation details, `6.4` CLI contract + failure behavior, `6.5` demo/reproducibility package.

## Q2) Does the system call any external LLM API at runtime?
- Runtime answer: **No** for the shipped detector package.
- Current runtime path (`jbd` -> `Predictor` -> `RulesDetector|LoraDetector`) does not call OpenAI/Anthropic/Together/Groq APIs.
- Evidence:
  - `src/llm_jailbreak_detector/cli.py`
  - `src/llm_jailbreak_detector/predict.py`
  - `src/llm_jailbreak_detector/lora_detector.py` (`local_files_only=True`)
  - `src/llm_jailbreak_detector/rules_detector.py`
- Clarification:
  - `external/BIPIA/config/*.yaml` includes OpenAI placeholders, but these are dataset-research artifacts and not used by `jbd` runtime inference.

## Q3) What is the expected primary demo mode?
- Primary demo mode: **CLI-only local run**.
- Justification:
  - packaged CLI entrypoint exists (`pyproject.toml` -> `jbd = llm_jailbreak_detector.cli:main`);
  - commands are already documented and test-covered;
  - no service layer (FastAPI/Flask) is implemented in this repo.
- Evidence:
  - `pyproject.toml`
  - `src/llm_jailbreak_detector/cli.py`
  - `tests/test_cli_smoke.py`
  - `docs/DEMO_GUIDE.md`

## Q4) Is there a demo video?
- Result: **No demo video link is present in the repository**.
- Checked locations:
  - `README.md`
  - `docs/DEMO_GUIDE.md`
  - `docs/User_Manual.md`
  - `thesis/06_system_demo.md`
- Action taken:
  - provided scripted live demo package:
    - `demo/DEMO_SCRIPT.md`
    - `demo/README.md`
    - `demo/sample_inputs.jsonl`
    - `demo/expected_outputs.jsonl`

## Q5) Is the shipped detector single-model or ensemble?
- Runtime architecture is **single selected detector per invocation**, not an ensemble.
- Selection is explicit via CLI flag `--detector rules|lora`.
- Evidence:
  - `src/llm_jailbreak_detector/cli.py` (`choices=["rules","lora"]`)
  - `src/llm_jailbreak_detector/predict.py` (`Predictor.__init__` chooses one backend)
- Operational consequence:
  - there is no score fusion or stacking logic in runtime prediction path.
