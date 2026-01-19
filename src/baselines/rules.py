from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Tuple

# Week-1 baseline: intentionally simple. Improve later.
DEFAULT_PATTERNS = [
    r"ignore (all|previous) instructions",
    r"system prompt",
    r"you are now",
    r"jailbreak",
    r"do anything now",
    r"developer message",
]

@dataclass
class RulesConfig:
    patterns: List[str]

class RulesDetector:
    def __init__(self, config: RulesConfig | None = None) -> None:
        self.config = config or RulesConfig(patterns=DEFAULT_PATTERNS)
        self._compiled = [re.compile(pat, re.IGNORECASE) for pat in self.config.patterns]

    def score(self, text: str) -> float:
        # Returns a risk score in [0,1].
        # Simple: if any pattern matches, risk=1 else 0.
        for rx in self._compiled:
            if rx.search(text):
                return 1.0
        return 0.0
