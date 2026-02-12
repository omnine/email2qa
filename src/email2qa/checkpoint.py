from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict


class Checkpoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    last_sent_at: datetime
    last_message_id: str


def checkpoint_path(base_dir: str) -> Path:
    return Path(base_dir).resolve() / "checkpoint.json"


def load_checkpoint(path: Path) -> Checkpoint | None:
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return Checkpoint.model_validate(data)


def write_checkpoint(path: Path, checkpoint: Checkpoint) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(checkpoint.model_dump(mode="json"), handle, indent=2)


def reset_checkpoint(path: Path) -> bool:
    if not path.exists():
        return False
    path.unlink()
    return True
