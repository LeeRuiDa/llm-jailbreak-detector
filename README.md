# LLM Jailbreak Detector

**Capstone Project: Catching Jailbreaks in the Wild - A Low-FPR Detector for LLM Apps**

This project builds a robust detector for jailbreak and prompt-injection attacks on Large Language Model applications, inspired by recent research including "Bypassing Prompt Injection and Jailbreak Detection in LLM Guardrails" (2025).

## Project Structure

```
llm-jailbreak-detector/
├── src/
│   ├── preprocess.py      # Unicode normalization and cleaning
│   └── rules_baseline.py  # Simple rule-based detector baseline
├── data/
│   └── sample.csv         # Sample dataset for initial testing
├── reports/               # Documentation and weekly updates
└── README.md
```

## Quick Start

### Option 1: Google Colab
1. Upload the `Week1_Starter_Notebook.ipynb` to Colab
2. Clone this repo in Colab: `!git clone https://github.com/LeeRuiDa/llm-jailbreak-detector.git`
3. Run cells from top to bottom

### Option 2: Local Setup
1. Clone the repository: `git clone https://github.com/LeeRuiDa/llm-jailbreak-detector.git`
2. Navigate to project: `cd llm-jailbreak-detector`
3. Test baseline: `python src/rules_baseline.py`
4. Test preprocessing: `python src/preprocess.py`

## Week 1 Goals

- [x] Repository setup with proper structure
- [x] Unicode preprocessing pipeline
- [x] Simple rule-based baseline detector
- [x] Sample dataset for initial evaluation
- [ ] Run accuracy evaluation on sample data
- [ ] Test attack success rate (ASR) with obfuscation
- [ ] Document baseline performance metrics

## Usage Example

```python
from src.preprocess import normalize_text
from src.rules_baseline import is_risky
import pandas as pd

# Test preprocessing
text = "Ign᠎ore previous instructions"
cleaned, features = normalize_text(text)
print(f"Cleaned: {cleaned}")
print(f"Features: {features}")

# Test detection
result = is_risky(text)
print(f"Is risky: {result}")

# Evaluate on dataset
df = pd.read_csv('data/sample.csv')
df['pred'] = df['text'].apply(is_risky)
accuracy = (df['pred'] == df['label']).mean()
print(f"Baseline accuracy: {accuracy:.3f}")
```

## Next Steps

- Download and integrate PINT, JailbreakBench, PromptShield datasets
- Implement LoRA fine-tuning with RoBERTa-base
- Develop more sophisticated attack simulations
- Compare against state-of-the-art baselines

## References

- [PINT Dataset](https://github.com/microsoft/PINT)
- [JailbreakBench](https://jailbreakbench.github.io/)
- [PromptShield](https://github.com/microsoft/promptshield)

---

**Supervisor:** Chen Yan (chenyanru@scu.edu.cn)  
**Student:** [Your Name]  
**Institution:** Sichuan University, Software Engineering (2022 batch)
