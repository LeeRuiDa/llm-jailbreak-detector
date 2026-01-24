"""Installable package wrapper for the jailbreak detector."""
from __future__ import annotations

from .normalize import normalize_text
from .predict import Predictor, predict
from .rules_detector import RulesDetector

__all__ = [
    "Predictor",
    "RulesDetector",
    "normalize_text",
    "predict",
]
