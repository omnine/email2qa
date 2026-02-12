from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class QaRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=8)
    answer: str = Field(min_length=12)
    confidence: float = Field(ge=0.0, le=1.0)
    extraction_notes: str = Field(default="")

    message_id: str = Field(min_length=1)
    thread_id: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    sent_at: datetime
    sender: str = Field(min_length=1)
    recipients: list[str] = Field(default_factory=list)

    @field_validator("question", "answer", "extraction_notes")
    @classmethod
    def _normalize_text(cls, value: str) -> str:
        return " ".join(value.split()).strip()


class RejectedRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str
    message_id: str
    thread_id: str
    subject: str
    sent_at: datetime
    candidate_question: str = ""
    candidate_answer: str = ""


class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    started_at: datetime
    finished_at: datetime
    total_processed: int
    accepted_count: int
    rejected_count: int
    dry_run: bool
    model: str
    min_confidence: float
