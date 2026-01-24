from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LoraDetector:
    """LoRA-backed detector that loads local artifacts only."""

    def __init__(self, run_dir: str | Path, device: str = "cpu") -> None:
        if not run_dir:
            raise ValueError("run_dir is required for lora detector")
        self.run_dir = Path(run_dir)
        if not self.run_dir.exists():
            raise FileNotFoundError(f"run_dir not found: {self.run_dir}")
        config_path = self.run_dir / "config.json"
        if not config_path.is_file():
            raise FileNotFoundError(f"Missing config.json in {self.run_dir}")
        self.config = self._load_config(config_path)
        self.threshold = self._load_threshold(self.config)
        self.attack_class_index = int(self.config.get("attack_class_index", 1))
        self.max_length = int(self.config.get("max_length", 256))
        self.model_name = self.config.get("model_name") or self.config.get("backbone")
        if not self.model_name:
            raise ValueError("config.json must include model_name or backbone")
        self.device = device
        self._model = None
        self._tokenizer = None

    @staticmethod
    def _load_config(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    @staticmethod
    def _load_threshold(config: dict[str, Any]) -> float:
        if "val_threshold" in config:
            return float(config["val_threshold"])
        if "threshold" in config:
            return float(config["threshold"])
        return 0.5

    def _load_model(self) -> None:
        if self._model is not None:
            return
        try:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            from peft import PeftModel
            import torch
        except ImportError as exc:
            raise RuntimeError(
                "LoRA dependencies not installed. Run pip install .[lora]."
            ) from exc

        adapter_dir = self.run_dir / "lora_adapter"
        if not adapter_dir.exists():
            raise FileNotFoundError(
                f"Missing lora_adapter in {self.run_dir}. Provide a valid run_dir or use rules."
            )
        try:
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, local_files_only=True
            )
            base_model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name, local_files_only=True
            )
            self._model = PeftModel.from_pretrained(
                base_model, str(adapter_dir), local_files_only=True
            )
        except OSError as exc:
            raise RuntimeError(
                "Failed to load local model files. Ensure the HF cache is populated or "
                "provide local weights in the cache."
            ) from exc
        self._model.to(self.device)
        self._model.eval()

    def predict_proba(self, text: str) -> float:
        self._load_model()
        if self._model is None or self._tokenizer is None:
            raise RuntimeError("Model failed to initialize")
        import torch

        inputs = self._tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self._model(**inputs)
            logits = outputs.logits
            if logits.shape[-1] == 1:
                score = torch.sigmoid(logits)[0].item()
            else:
                probs = torch.softmax(logits, dim=-1)
                score = probs[0, self.attack_class_index].item()
        return float(score)

    def predict(self, text: str, threshold: float | None = None) -> int:
        if threshold is None:
            threshold = self.threshold
        score = self.predict_proba(text)
        return int(score >= threshold)
