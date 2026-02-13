from __future__ import annotations

import argparse
from datetime import datetime, timezone

from dateutil.parser import isoparse

from email2qa.checkpoint import checkpoint_path, load_checkpoint, reset_checkpoint
from email2qa.config import RunOptions, get_output_dir, load_config
from email2qa.pipeline import run_pipeline


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = isoparse(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def confirm_checkpoint_reset(force: bool, input_fn=input) -> bool:
    if force:
        return True
    answer = input_fn("Type RESET to confirm checkpoint deletion: ").strip()
    return answer == "RESET"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract Q&A pairs from Exchange Sent Items")
    parser.add_argument("--since", type=str, default=None, help="Start date (ISO-8601)")
    parser.add_argument("--until", type=str, default=None, help="End date (ISO-8601)")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of emails")
    parser.add_argument("--dry-run", action="store_true", help="Skip LLM call and only run pipeline checks")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-step progress and outcomes while processing",
    )
    parser.add_argument(
        "--resume",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Resume from output checkpoint file",
    )
    parser.add_argument(
        "--checkpoint-inspect",
        action="store_true",
        help="Print current checkpoint and exit",
    )
    parser.add_argument(
        "--checkpoint-reset",
        action="store_true",
        help="Delete current checkpoint and exit",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt for destructive actions",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    output_dir = get_output_dir()
    checkpoint_file = checkpoint_path(output_dir)
    if args.checkpoint_inspect:
        checkpoint = load_checkpoint(checkpoint_file)
        if checkpoint is None:
            print(f"No checkpoint found at: {checkpoint_file}")
        else:
            print(checkpoint.model_dump_json(indent=2))
        return

    if args.checkpoint_reset:
        if not confirm_checkpoint_reset(args.force):
            print("Checkpoint reset canceled.")
            return
        deleted = reset_checkpoint(checkpoint_file)
        if deleted:
            print(f"Checkpoint deleted: {checkpoint_file}")
        else:
            print(f"No checkpoint found to delete at: {checkpoint_file}")
        return

    config = load_config()
    options = RunOptions(
        since=_parse_datetime(args.since),
        until=_parse_datetime(args.until),
        limit=args.limit,
        dry_run=args.dry_run,
        resume=args.resume,
        verbose=args.verbose,
    )

    output_dir = run_pipeline(config, options)
    print(f"Run completed. Output: {output_dir}")


if __name__ == "__main__":
    main()
