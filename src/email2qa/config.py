from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AppConfig:
    exchange_server: str
    exchange_email: str
    exchange_username: str
    exchange_password: str
    ollama_base_url: str
    ollama_model: str
    output_dir: str
    min_confidence: float


@dataclass(frozen=True)
class RunOptions:
    since: datetime | None = None
    until: datetime | None = None
    limit: int | None = None
    dry_run: bool = False
    resume: bool = True


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def load_config() -> AppConfig:
    email = _required("EMAIL2QA_EXCHANGE_EMAIL")
    return AppConfig(
        exchange_server=_required("EMAIL2QA_EXCHANGE_SERVER"),
        exchange_email=email,
        exchange_username=os.getenv("EMAIL2QA_EXCHANGE_USERNAME", email).strip() or email,
        exchange_password=_required("EMAIL2QA_EXCHANGE_PASSWORD"),
        ollama_base_url=os.getenv("EMAIL2QA_OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
        ollama_model=os.getenv("EMAIL2QA_OLLAMA_MODEL", "gemma3:4b").strip(),
        output_dir=os.getenv("EMAIL2QA_OUTPUT_DIR", "./output").strip(),
        min_confidence=float(os.getenv("EMAIL2QA_MIN_CONFIDENCE", "0.65")),
    )


def get_output_dir() -> str:
    return os.getenv("EMAIL2QA_OUTPUT_DIR", "./output").strip()
