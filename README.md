# email2qa

`email2qa` extracts high-quality Question/Answer pairs from Exchange `Sent Items` and writes auditable JSONL output.

## MVP scope

- Source: Exchange `Sent Items`
- Output: JSONL records with schema + source metadata
- Model: Local Ollama model (configurable)
- Auth: Exchange basic auth/app password

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```powershell
pip install -e .[dev]
```

3. Copy `.env.example` values into your shell/session.

## Environment variables

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

```powershell
python -m email2qa.main --dry-run --limit 20
```

Live run:

```powershell
python -m email2qa.main --since 2026-01-01 --limit 100
```

Disable resume behavior for a full reprocess:

```powershell
python -m email2qa.main --no-resume --since 2026-01-01 --limit 100
```

Inspect current checkpoint:

```powershell
python -m email2qa.main --checkpoint-inspect
```

Reset current checkpoint:

```powershell
python -m email2qa.main --checkpoint-reset
```

## Output files

Each run writes to a timestamped folder under `EMAIL2QA_OUTPUT_DIR`:

- `accepted.jsonl` - accepted Q&A records
- `rejected.jsonl` - rejected items with reasons
- `manifest.json` - run metrics and settings

Checkpoint state is persisted at `EMAIL2QA_OUTPUT_DIR/checkpoint.json`.
By default, runs resume from the last processed `(sent_at, message_id)` to avoid reprocessing prior emails.
