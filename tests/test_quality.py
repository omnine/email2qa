from datetime import datetime, timezone

from email2qa.exchange_client import SourceEmail
from email2qa.llm_client import LlmResult
from email2qa.quality import evaluate_candidate, new_quality_state


def _message() -> SourceEmail:
    return SourceEmail(
        message_id="m1",
        thread_id="t1",
        subject="Re: Account",
        body="sample",
        sent_at=datetime.now(timezone.utc),
        sender="agent@example.com",
        recipients=["user@example.com"],
    )


def test_low_confidence_is_rejected() -> None:
    qa, rejected = evaluate_candidate(
        message=_message(),
        candidate=LlmResult(question="How to login?", answer="Use SSO.", confidence=0.3, extraction_notes=""),
        min_confidence=0.65,
        state=new_quality_state(),
    )
    assert qa is None
    assert rejected is not None
    assert rejected.reason.startswith("low_confidence")


def test_duplicate_is_rejected() -> None:
    state = new_quality_state()
    candidate = LlmResult(
        question="How do I update billing?",
        answer="Open billing page and save changes.",
        confidence=0.95,
        extraction_notes="",
    )

    qa1, rejected1 = evaluate_candidate(
        message=_message(),
        candidate=candidate,
        min_confidence=0.65,
        state=state,
    )
    assert qa1 is not None
    assert rejected1 is None

    qa2, rejected2 = evaluate_candidate(
        message=_message(),
        candidate=candidate,
        min_confidence=0.65,
        state=state,
    )
    assert qa2 is None
    assert rejected2 is not None
    assert rejected2.reason == "duplicate_pair"
