from datetime import datetime, timezone
from pathlib import Path

from email2qa.checkpoint import Checkpoint, load_checkpoint, write_checkpoint


def test_checkpoint_roundtrip(tmp_path: Path) -> None:
    checkpoint_path = tmp_path / "checkpoint.json"
    checkpoint = Checkpoint(
        last_sent_at=datetime(2026, 2, 1, 10, 30, tzinfo=timezone.utc),
        last_message_id="abc-123",
    )

    write_checkpoint(checkpoint_path, checkpoint)
    loaded = load_checkpoint(checkpoint_path)

    assert loaded is not None
    assert loaded.last_sent_at == checkpoint.last_sent_at
    assert loaded.last_message_id == checkpoint.last_message_id


def test_load_checkpoint_missing_file_returns_none(tmp_path: Path) -> None:
    checkpoint_path = tmp_path / "not-found.json"
    assert load_checkpoint(checkpoint_path) is None
