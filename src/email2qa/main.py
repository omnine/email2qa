from __future__ import annotations

import argparse
from datetime import date

from dateutil.parser import isoparse

from email2qa.config import RunOptions, load_config
from email2qa.pipeline import run_pipeline


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return isoparse(value).date()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract Q&A pairs from Exchange Sent Items")
    parser.add_argument("--since", type=str, default=None, help="Start date (ISO-8601)")
    parser.add_argument("--until", type=str, default=None, help="End date (ISO-8601)")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of emails")
    parser.add_argument("--dry-run", action="store_true", help="Skip LLM call and only run pipeline checks")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    config = load_config()
    options = RunOptions(
        since=_parse_date(args.since),
        until=_parse_date(args.until),
        limit=args.limit,
        dry_run=args.dry_run,
    )

    output_dir = run_pipeline(config, options)
    print(f"Run completed. Output: {output_dir}")


if __name__ == "__main__":
    main()
