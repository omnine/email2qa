from __future__ import annotations

from email2qa.exchange_client import SourceEmail

SYSTEM_PROMPT = """You extract one user question and one support answer from an outbound support email.
Return STRICT JSON only. No markdown. No extra keys.
If no clear question/answer can be extracted, return empty strings and confidence 0.
"""


def build_user_prompt(message: SourceEmail, cleaned_text: str) -> str:
    return f"""
Extract a single best QA pair from this sent email.

Subject: {message.subject}
Sender: {message.sender}
Recipients: {", ".join(message.recipients)}
SentAt: {message.sent_at.isoformat()}
ThreadId: {message.thread_id}
MessageId: {message.message_id}

EmailBody:
{cleaned_text}

JSON schema:
{{
  "question": "string",
  "answer": "string",
  "confidence": 0.0,
  "extraction_notes": "string"
}}
""".strip()
