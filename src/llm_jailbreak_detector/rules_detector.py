from __future__ import annotations

from typing import Iterable

from baselines.rules import RulesConfig as _RulesConfig
from baselines.rules import RulesDetector as _RulesDetector


class RulesDetector:
    """Wrapper around the Week-1 rules baseline with predict helpers."""

    def __init__(self, patterns: Iterable[str] | None = None) -> None:
        config = _RulesConfig(patterns=list(patterns)) if patterns is not None else None
        self._detector = _RulesDetector(config=config)

    def predict_proba(self, text: str) -> float:
        return float(self._detector.score(text))

    def predict(self, text: str, threshold: float = 0.5) -> int:
        score = self.predict_proba(text)
        return int(score >= threshold)
