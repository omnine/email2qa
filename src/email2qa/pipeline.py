from __future__ import annotations

from datetime import datetime, timezone

from email2qa.checkpoint import Checkpoint, checkpoint_path, load_checkpoint, write_checkpoint
from email2qa.config import AppConfig, RunOptions
from email2qa.exchange_client import fetch_sent_items
from email2qa.llm_client import LlmResult, OllamaClient
from email2qa.output import append_jsonl, make_run_dir, write_manifest
from email2qa.preprocess import preprocess_email_body
from email2qa.prompts import build_user_prompt
from email2qa.quality import evaluate_candidate, new_quality_state
from email2qa.schema import Manifest, RejectedRecord


def run_pipeline(config: AppConfig, options: RunOptions) -> str:
    def log(message: str) -> None:
        if options.verbose:
            print(f"[verbose] {message}")

    started_at = datetime.now(timezone.utc)
    run_id, run_dir = make_run_dir(config.output_dir)
    checkpoint_file = checkpoint_path(config.output_dir)
    accepted_path = run_dir / "accepted.jsonl"
    rejected_path = run_dir / "rejected.jsonl"
    log(f"Run initialized (run_id={run_id}, output={run_dir})")

    checkpoint = load_checkpoint(checkpoint_file) if options.resume else None
    since = options.since
    if checkpoint and (since is None or checkpoint.last_sent_at > since):
        since = checkpoint.last_sent_at
    if options.resume:
        if checkpoint:
            log(
                "Loaded checkpoint "
                f"(last_sent_at={checkpoint.last_sent_at.isoformat()}, message_id={checkpoint.last_message_id})"
            )
        else:
            log("Resume enabled but no checkpoint file found")
    else:
        log("Resume disabled; processing from provided time window")

    log("Fetching sent items from Exchange")
    messages = fetch_sent_items(
        server=config.exchange_server,
        email=config.exchange_email,
        username=config.exchange_username,
        password=config.exchange_password,
        since=since,
        until=options.until,
        limit=options.limit,
    )
    log(f"Fetched {len(messages)} messages")

    state = new_quality_state()
    ollama = OllamaClient(config.ollama_base_url, config.ollama_model)
    log(
        f"Quality/LLM initialized (dry_run={options.dry_run}, model={config.ollama_model}, min_confidence={config.min_confidence})"
    )

    accepted = 0
    rejected = 0
    last_processed: tuple[datetime, str] | None = None

    for message in messages:
        log(f"Processing message {message.message_id} sent {message.sent_at.isoformat()}")
        if checkpoint and (message.sent_at, message.message_id) <= (
            checkpoint.last_sent_at,
            checkpoint.last_message_id,
        ):
            log(f"Skipped by checkpoint: {message.message_id}")
            continue

        if last_processed is None or (message.sent_at, message.message_id) > last_processed:
            last_processed = (message.sent_at, message.message_id)

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
            log(f"Rejected {message.message_id}: insufficient_content")
            continue
        log(f"Preprocess passed for {message.message_id}")

        if options.dry_run:
            candidate = LlmResult(
                question="",
                answer="",
                confidence=0.0,
                extraction_notes="dry_run",
            )
            log(f"LLM step skipped for {message.message_id} (dry-run)")
        else:
            prompt = build_user_prompt(message, pre.cleaned_text)
            candidate = ollama.extract_qa(prompt)
            log(f"LLM extraction completed for {message.message_id} (confidence={candidate.confidence:.2f})")

        qa, reject = evaluate_candidate(
            message=message,
            candidate=candidate,
            min_confidence=config.min_confidence,
            state=state,
        )

        if qa:
            append_jsonl(accepted_path, qa)
            accepted += 1
            log(f"Accepted {message.message_id}")
        else:
            append_jsonl(rejected_path, reject)
            rejected += 1
            log(f"Rejected {message.message_id}: {reject.reason}")

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
    log("Manifest written")

    if last_processed:
        write_checkpoint(
            checkpoint_file,
            Checkpoint(last_sent_at=last_processed[0], last_message_id=last_processed[1]),
        )
        log(
            f"Checkpoint updated (last_sent_at={last_processed[0].isoformat()}, message_id={last_processed[1]})"
        )

    log(f"Run complete (accepted={accepted}, rejected={rejected}, total={len(messages)})")

    return str(run_dir)
