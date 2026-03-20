"""Configuration helpers for listener adapters."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class GmailIdleConfig:
    """Runtime configuration for the current Gmail IMAP IDLE adapter."""

    email: str = os.environ.get("GMAIL_EMAIL", "mc.agent.claw@gmail.com")
    password_file: Path = Path(
        os.environ.get(
            "GMAIL_APP_PASSWORD_FILE",
            str(Path.home() / ".openclaw" / "workspace" / "secrets" / "gmail-app-password.txt"),
        )
    )
    base_dir: Path = Path(
        os.environ.get(
            "MAIL_LISTENER_BASE_DIR",
            str(Path.home() / ".cache" / "mail-listener"),
        )
    )
    imap_server: str = "imap.gmail.com"
    imap_port: int = 993
    idle_refresh_seconds: int = int(os.environ.get("GMAIL_IDLE_REFRESH_SECONDS", str(29 * 60)))
    socket_timeout_seconds: float = float(os.environ.get("GMAIL_IDLE_SOCKET_TIMEOUT_SECONDS", "5"))
    heartbeat_interval_seconds: int = int(
        os.environ.get("GMAIL_IDLE_HEARTBEAT_INTERVAL_SECONDS", "300")
    )
    reconnect_base_delay_seconds: int = int(
        os.environ.get("GMAIL_IDLE_RECONNECT_BASE_DELAY_SECONDS", "5")
    )
    reconnect_max_delay_seconds: int = int(
        os.environ.get("GMAIL_IDLE_RECONNECT_MAX_DELAY_SECONDS", "300")
    )
    log_max_bytes: int = int(os.environ.get("GMAIL_IDLE_LOG_MAX_BYTES", str(5 * 1024 * 1024)))
    log_backup_count: int = int(os.environ.get("GMAIL_IDLE_LOG_BACKUP_COUNT", "5"))

    @property
    def runtime_dir(self) -> Path:
        return Path(os.environ.get("MAIL_LISTENER_RUNTIME_DIR", str(self.base_dir / "run")))

    @property
    def log_dir(self) -> Path:
        return Path(os.environ.get("MAIL_LISTENER_LOG_DIR", str(self.base_dir / "logs")))

    @property
    def log_file(self) -> Path:
        return Path(
            os.environ.get("MAIL_LISTENER_LOG_FILE", str(self.log_dir / "gmail_imap_idle.log"))
        )

    @property
    def pid_file(self) -> Path:
        return Path(
            os.environ.get("MAIL_LISTENER_PID_FILE", str(self.runtime_dir / "gmail_imap_idle.pid"))
        )
