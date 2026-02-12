from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel


def make_run_dir(base_dir: str) -> tuple[str, Path]:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path(base_dir).resolve() / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_id, run_dir


def append_jsonl(path: Path, model: BaseModel) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(model.model_dump_json())
        handle.write("\n")


def write_manifest(path: Path, content: BaseModel) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(content.model_dump(mode="json"), handle, indent=2)
