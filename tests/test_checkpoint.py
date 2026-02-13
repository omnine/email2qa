from datetime import datetime, timezone
from pathlib import Path

from email2qa.checkpoint import (
    Checkpoint,
    checkpoint_path,
    load_checkpoint,
    reset_checkpoint,
    write_checkpoint,
)


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
    assert loaded.last_sent_at.tzinfo is timezone.utc


def test_load_checkpoint_missing_file_returns_none(tmp_path: Path) -> None:
    checkpoint_path = tmp_path / "not-found.json"
    assert load_checkpoint(checkpoint_path) is None


def test_checkpoint_path_uses_base_dir(tmp_path: Path) -> None:
    computed = checkpoint_path(str(tmp_path))
    assert computed == tmp_path.resolve() / "checkpoint.json"


def test_reset_checkpoint_deletes_file(tmp_path: Path) -> None:
    path = tmp_path / "checkpoint.json"
    write_checkpoint(
        path,
        Checkpoint(last_sent_at=datetime(2026, 2, 1, tzinfo=timezone.utc), last_message_id="m1"),
    )

    deleted = reset_checkpoint(path)
    assert deleted is True
    assert path.exists() is False


def test_reset_checkpoint_missing_file_returns_false(tmp_path: Path) -> None:
    path = tmp_path / "checkpoint.json"
    deleted = reset_checkpoint(path)
    assert deleted is False
