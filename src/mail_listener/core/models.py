"""Provider-neutral models used by the current listener implementation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ListenerStats:
    reconnect_attempt: int = 0
    total_connections: int = 0
    total_mail_events: int = 0
    last_heartbeat_at: float = 0.0
