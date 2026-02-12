from __future__ import annotations

import json
from dataclasses import dataclass

import requests

from email2qa.prompts import SYSTEM_PROMPT


@dataclass(frozen=True)
class LlmResult:
    question: str
    answer: str
    confidence: float
    extraction_notes: str


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout_seconds: int = 60) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout_seconds

    @property
    def model(self) -> str:
        return self._model

    def extract_qa(self, prompt: str) -> LlmResult:
        payload = {
            "model": self._model,
            "format": "json",
            "stream": False,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        }

        response = requests.post(
            f"{self._base_url}/api/chat",
            json=payload,
            timeout=self._timeout,
        )
        response.raise_for_status()
        body = response.json()

        content = body.get("message", {}).get("content", "{}").strip() or "{}"
        parsed = json.loads(content)

        return LlmResult(
            question=str(parsed.get("question", "")).strip(),
            answer=str(parsed.get("answer", "")).strip(),
            confidence=float(parsed.get("confidence", 0.0)),
            extraction_notes=str(parsed.get("extraction_notes", "")).strip(),
        )
