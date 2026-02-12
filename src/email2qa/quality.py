from __future__ import annotations

from dataclasses import dataclass

from pydantic import ValidationError

from email2qa.exchange_client import SourceEmail
from email2qa.llm_client import LlmResult
from email2qa.schema import QaRecord, RejectedRecord


@dataclass
class QualityState:
    seen_pairs: set[tuple[str, str]]


def new_quality_state() -> QualityState:
    return QualityState(seen_pairs=set())


def evaluate_candidate(
    *,
    message: SourceEmail,
    candidate: LlmResult,
    min_confidence: float,
    state: QualityState,
) -> tuple[QaRecord | None, RejectedRecord | None]:
    if not candidate.question or not candidate.answer:
        return None, _reject(message, "missing_question_or_answer", candidate)

    if candidate.confidence < min_confidence:
        return None, _reject(message, f"low_confidence:{candidate.confidence:.2f}", candidate)

    dedupe_key = (_normalize_key(candidate.question), _normalize_key(candidate.answer))
    if dedupe_key in state.seen_pairs:
        return None, _reject(message, "duplicate_pair", candidate)

    try:
        qa = QaRecord(
            question=candidate.question,
            answer=candidate.answer,
            confidence=candidate.confidence,
            extraction_notes=candidate.extraction_notes,
            message_id=message.message_id,
            thread_id=message.thread_id,
            subject=message.subject,
            sent_at=message.sent_at,
            sender=message.sender,
            recipients=message.recipients,
        )
    except ValidationError:
        return None, _reject(message, "schema_validation_failed", candidate)

    state.seen_pairs.add(dedupe_key)
    return qa, None


def _normalize_key(value: str) -> str:
    return " ".join(value.lower().split())


def _reject(message: SourceEmail, reason: str, candidate: LlmResult) -> RejectedRecord:
    return RejectedRecord(
        reason=reason,
        message_id=message.message_id,
        thread_id=message.thread_id,
        subject=message.subject,
        sent_at=message.sent_at,
        candidate_question=candidate.question,
        candidate_answer=candidate.answer,
    )
