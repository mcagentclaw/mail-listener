"""Normalized event structures."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class MailMessageReceivedEvent:
    event_type: str
    provider: str
    mailbox: str
    exists_count: int
    previous_exists_count: int
    received_at: str

    @classmethod
    def from_exists_counts(
        cls,
        *,
        provider: str,
        mailbox: str,
        exists_count: int,
        previous_exists_count: int,
    ) -> "MailMessageReceivedEvent":
        return cls(
            event_type="mail.message.received",
            provider=provider,
            mailbox=mailbox,
            exists_count=exists_count,
            previous_exists_count=previous_exists_count,
            received_at=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
