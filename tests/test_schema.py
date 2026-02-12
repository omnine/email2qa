from datetime import datetime, timezone

from email2qa.schema import QaRecord


def test_qarecord_normalizes_whitespace() -> None:
    record = QaRecord(
        question="  How   do I reset password?  ",
        answer="  Use the reset link in portal.   ",
        confidence=0.8,
        extraction_notes="  extracted from response   ",
        message_id="m1",
        thread_id="t1",
        subject="Re: Login",
        sent_at=datetime.now(timezone.utc),
        sender="agent@example.com",
        recipients=["user@example.com"],
    )

    assert record.question == "How do I reset password?"
    assert record.answer == "Use the reset link in portal."
    assert record.extraction_notes == "extracted from response"
