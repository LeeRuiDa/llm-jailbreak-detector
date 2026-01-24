from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .normalize import normalize_text
from .rules_detector import RulesDetector


@dataclass
class PredictionResult:
    score: float
    label: int
    threshold: float
    detector: str
    metadata: dict[str, Any]


class Predictor:
    """Unified predictor for rules or LoRA detectors."""

    def __init__(self, detector: str = "rules", run_dir: str | None = None) -> None:
        detector = detector.lower()
        if detector not in {"rules", "lora"}:
            raise ValueError(f"Unknown detector: {detector}")
        self.detector_name = detector
        if detector == "rules":
            self.detector = RulesDetector()
        else:
            if not run_dir:
                raise ValueError("run_dir is required for lora detector")
            from .lora_detector import LoraDetector

            self.detector = LoraDetector(run_dir)

    def _resolve_threshold(self, threshold: float | str | None) -> tuple[float, str]:
        if threshold is None:
            if self.detector_name == "lora":
                return self.detector.threshold, "config"
            return 0.5, "default"
        if isinstance(threshold, str):
            if threshold.lower() != "val":
                raise ValueError("threshold must be a float or 'val'")
            if self.detector_name != "lora":
                raise ValueError("threshold='val' is only valid for lora")
            return self.detector.threshold, "val"
        return float(threshold), "user"

    def predict(
        self,
        text: str,
        *,
        threshold: float | str | None = None,
        normalize_infer: bool = False,
        drop_mn: bool = False,
    ) -> PredictionResult:
        inference_text = (
            normalize_text(text, drop_mn=drop_mn) if normalize_infer else text
        )
        resolved_threshold, threshold_source = self._resolve_threshold(threshold)
        score = self.detector.predict_proba(inference_text)
        label = int(score >= resolved_threshold)
        metadata = {
            "threshold_source": threshold_source,
            "normalize_infer": normalize_infer,
            "drop_mn": drop_mn,
        }
        if self.detector_name == "lora":
            metadata["run_dir"] = str(self.detector.run_dir)
            metadata["model_name"] = self.detector.model_name
        return PredictionResult(
            score=score,
            label=label,
            threshold=resolved_threshold,
            detector=self.detector_name,
            metadata=metadata,
        )


def predict(
    text: str,
    *,
    detector: str = "rules",
    run_dir: str | None = None,
    threshold: float | str | None = None,
    normalize_infer: bool = False,
    drop_mn: bool = False,
) -> dict[str, Any]:
    predictor = Predictor(detector=detector, run_dir=run_dir)
    result = predictor.predict(
        text,
        threshold=threshold,
        normalize_infer=normalize_infer,
        drop_mn=drop_mn,
    )
    return {
        "score": result.score,
        "label": result.label,
        "threshold": result.threshold,
        "detector": result.detector,
        "metadata": result.metadata,
    }
