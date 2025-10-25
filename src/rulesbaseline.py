import re

def detect_jailbreak(prompt):
    # Simple rule-based detection (expandable)
    risky = [r"jailbreak", r"ignore previous", r"bypass guard" ]
    for pat in risky:
        if re.search(pat, prompt, re.IGNORECASE):
            return True
    return False

if __name__ == '__main__':
    test_prompts = [
        "jailbreak the model",
        "just a normal prompt",
        "please bypass guardrails"
    ]
    for p in test_prompts:
        print(f"{p}: {detect_jailbreak(p)}")
