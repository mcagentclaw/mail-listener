from __future__ import annotations

from pathlib import Path

from mail_listener.adapters.gmail.idle import GmailIdleDaemon, build_parser
from mail_listener.core.config import GmailIdleConfig


def make_config(tmp_path: Path) -> GmailIdleConfig:
    password_file = tmp_path / "gmail-app-password.txt"
    password_file.write_text("abcd efgh ijkl mnop\n", encoding="utf-8")
    return GmailIdleConfig(
        email="listener@example.test",
        password_file=password_file,
        base_dir=tmp_path,
        heartbeat_interval_seconds=30,
        reconnect_base_delay_seconds=5,
        reconnect_max_delay_seconds=300,
    )


def test_load_password_strips_whitespace(tmp_path: Path) -> None:
    daemon = GmailIdleDaemon(config=make_config(tmp_path))
    assert daemon.load_password() == "abcdefghijklmnop"


def test_compute_reconnect_delay_caps_at_max(tmp_path: Path) -> None:
    daemon = GmailIdleDaemon(config=make_config(tmp_path))
    assert daemon.compute_reconnect_delay(1) == 5
    assert daemon.compute_reconnect_delay(3) == 20
    assert daemon.compute_reconnect_delay(10) == 300


def test_parse_exists_and_event_shape(tmp_path: Path) -> None:
    daemon = GmailIdleDaemon(config=make_config(tmp_path))
    assert daemon.parse_exists("* 42 EXISTS") == 42
    event = daemon.build_received_event(exists_count=42, previous_count=41)
    payload = event.to_dict()
    assert payload["event_type"] == "mail.message.received"
    assert payload["provider"] == "gmail-imap-idle"
    assert payload["mailbox"] == "listener@example.test"
    assert payload["exists_count"] == 42
    assert payload["previous_exists_count"] == 41


def test_build_parser_supports_check_flag() -> None:
    args = build_parser().parse_args(["--check"])
    assert args.check is True
