from __future__ import annotations

from datetime import datetime, timezone

from email2qa.config import AppConfig, RunOptions
from email2qa.exchange_client import fetch_sent_items
from email2qa.llm_client import LlmResult, OllamaClient
from email2qa.output import append_jsonl, make_run_dir, write_manifest
from email2qa.preprocess import preprocess_email_body
from email2qa.prompts import build_user_prompt
from email2qa.quality import evaluate_candidate, new_quality_state
from email2qa.schema import Manifest, RejectedRecord


def run_pipeline(config: AppConfig, options: RunOptions) -> str:
    started_at = datetime.now(timezone.utc)
    run_id, run_dir = make_run_dir(config.output_dir)
    accepted_path = run_dir / "accepted.jsonl"
    rejected_path = run_dir / "rejected.jsonl"

    messages = fetch_sent_items(
        server=config.exchange_server,
        email=config.exchange_email,
        username=config.exchange_username,
        password=config.exchange_password,
        since=options.since,
        until=options.until,
        limit=options.limit,
    )

    state = new_quality_state()
    ollama = OllamaClient(config.ollama_base_url, config.ollama_model)

    accepted = 0
    rejected = 0

    for message in messages:
        pre = preprocess_email_body(message.body)
        if not pre.has_enough_content:
            reject = RejectedRecord(
                reason="insufficient_content",
                message_id=message.message_id,
                thread_id=message.thread_id,
                subject=message.subject,
                sent_at=message.sent_at,
            )
            append_jsonl(rejected_path, reject)
            rejected += 1
            continue

        if options.dry_run:
            candidate = LlmResult(
                question="",
                answer="",
                confidence=0.0,
                extraction_notes="dry_run",
            )
        else:
            prompt = build_user_prompt(message, pre.cleaned_text)
            candidate = ollama.extract_qa(prompt)

        qa, reject = evaluate_candidate(
            message=message,
            candidate=candidate,
            min_confidence=config.min_confidence,
            state=state,
        )

        if qa:
            append_jsonl(accepted_path, qa)
            accepted += 1
        else:
            append_jsonl(rejected_path, reject)
            rejected += 1

    finished_at = datetime.now(timezone.utc)
    manifest = Manifest(
        run_id=run_id,
        started_at=started_at,
        finished_at=finished_at,
        total_processed=len(messages),
        accepted_count=accepted,
        rejected_count=rejected,
        dry_run=options.dry_run,
        model=config.ollama_model,
        min_confidence=config.min_confidence,
    )
    write_manifest(run_dir / "manifest.json", manifest)

    return str(run_dir)
