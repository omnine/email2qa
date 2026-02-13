# email2qa

`email2qa` extracts high-quality Question/Answer pairs from Exchange `Sent Items` and writes auditable JSONL output.

## MVP scope

- Source: Exchange `Sent Items`
- Output: JSONL records with schema + source metadata
- Model: Local Ollama model (configurable)
- Auth: Exchange basic auth/app password

## Setup

Ubuntu quick setup:

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
cp .env.example .env
```

Re-activate the environment later with:

```bash
source .venv/bin/activate
```

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -e .[dev]
```

3. Copy `.env.example` values into your shell/session.
4. (optional) Create a local `.env` file from `.env.example` — the project uses `python-dotenv` to load it automatically at runtime.

## Environment variables

The application will automatically load a local `.env` file (via `python-dotenv`) if present; shell environment variables take precedence.

- `EMAIL2QA_EXCHANGE_SERVER` (e.g. `mail.example.com`)
- `EMAIL2QA_EXCHANGE_EMAIL`
- `EMAIL2QA_EXCHANGE_USERNAME` (optional, defaults to email)
- `EMAIL2QA_EXCHANGE_PASSWORD`
- `EMAIL2QA_OLLAMA_BASE_URL` (default: `http://localhost:11434`)
- `EMAIL2QA_OLLAMA_MODEL` (default: `gemma3:4b`)
- `EMAIL2QA_OUTPUT_DIR` (default: `./output`)
- `EMAIL2QA_MIN_CONFIDENCE` (default: `0.65`)

## Usage

Dry run (no LLM calls):

```bash
python -m email2qa.main --dry-run --limit 20
```

Live run:

```bash
python -m email2qa.main --since 2026-01-01 --limit 100
```

Live run with step-by-step logging:

```bash
python -m email2qa.main --verbose --since 2026-01-01 --limit 100
```

Example verbose output:

Note: IDs, counts, and timestamps in this example vary per run.

```text
[verbose] Run initialized (run_id=20260213T120000Z, output=/path/to/output/20260213T120000Z)
[verbose] Loaded checkpoint (last_sent_at=2026-02-12T09:15:00+00:00, message_id=abc-123)
[verbose] Fetching sent items from Exchange
[verbose] Fetched 42 messages
[verbose] Processing message msg-001 sent 2026-02-12T10:03:22+00:00
[verbose] Preprocess passed for msg-001
[verbose] LLM extraction completed for msg-001 (confidence=0.81)
[verbose] Accepted msg-001
[verbose] Manifest written
[verbose] Run complete (accepted=30, rejected=12, total=42)
```

Disable resume behavior for a full reprocess:

```bash
python -m email2qa.main --no-resume --since 2026-01-01 --limit 100
```

Inspect current checkpoint:

```bash
python -m email2qa.main --checkpoint-inspect
```

Reset current checkpoint:

```bash
python -m email2qa.main --checkpoint-reset
```

Skip reset confirmation prompt:

```bash
python -m email2qa.main --checkpoint-reset --force
```

## Output files

Each run writes to a timestamped folder under `EMAIL2QA_OUTPUT_DIR`:

- `accepted.jsonl` - accepted Q&A records
- `rejected.jsonl` - rejected items with reasons
- `manifest.json` - run metrics and settings

Checkpoint state is persisted at `EMAIL2QA_OUTPUT_DIR/checkpoint.json`.
By default, runs resume from the last processed `(sent_at, message_id)` to avoid reprocessing prior emails.
