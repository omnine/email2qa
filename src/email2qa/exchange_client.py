from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time


@dataclass(frozen=True)
class SourceEmail:
    message_id: str
    thread_id: str
    subject: str
    body: str
    sent_at: datetime
    sender: str
    recipients: list[str]


def fetch_sent_items(
    *,
    server: str,
    email: str,
    username: str,
    password: str,
    since: date | None,
    until: date | None,
    limit: int | None,
) -> list[SourceEmail]:
    try:
        from exchangelib import Account, Configuration, Credentials, DELEGATE
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("exchangelib is required for Exchange ingestion") from exc

    credentials = Credentials(username=username, password=password)
    config = Configuration(server=server, credentials=credentials)
    account = Account(primary_smtp_address=email, config=config, autodiscover=False, access_type=DELEGATE)

    query = account.sent.all().order_by("-datetime_sent")
    if since:
        query = query.filter(datetime_sent__gte=datetime.combine(since, time.min))
    if until:
        query = query.filter(datetime_sent__lte=datetime.combine(until, time.max))
    if limit and limit > 0:
        query = query[:limit]

    records: list[SourceEmail] = []
    for item in query:
        recipients = [addr.email_address for addr in (item.to_recipients or []) if addr and addr.email_address]
        sender = item.sender.email_address if item.sender else email
        records.append(
            SourceEmail(
                message_id=str(item.message_id or item.id),
                thread_id=str(item.conversation_id.id if item.conversation_id else item.id),
                subject=(item.subject or "(no subject)").strip(),
                body=item.body if isinstance(item.body, str) else str(item.body),
                sent_at=item.datetime_sent,
                sender=sender,
                recipients=recipients,
            )
        )
    return records
