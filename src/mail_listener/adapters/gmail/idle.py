"""Current Gmail IMAP IDLE adapter packaged for mail-listener."""

from __future__ import annotations

import argparse
import atexit
from dataclasses import dataclass, field
import errno
import fcntl
import imaplib
import logging
from logging.handlers import RotatingFileHandler
import os
import signal
import socket
import ssl
import sys
import time
from typing import Optional

from mail_listener.core.config import GmailIdleConfig
from mail_listener.core.models import ListenerStats
from mail_listener.events.models import MailMessageReceivedEvent


class AlreadyRunningError(RuntimeError):
    """Raised when a pid lock is already held by a live process."""


class IdleRejectedError(RuntimeError):
    """Raised when the IMAP server rejects IDLE."""


@dataclass
class GmailIdleDaemon:
    """Foreground IMAP IDLE daemon suitable for process supervisors."""

    config: GmailIdleConfig = field(default_factory=GmailIdleConfig)

    def __post_init__(self) -> None:
        self.running = True
        self.stats = ListenerStats()
        self.logger = logging.getLogger("mail_listener.gmail_idle")
        self._pid_fd: Optional[int] = None

    def configure_logging(self, verbose: bool = False) -> None:
        self.config.log_file.parent.mkdir(parents=True, exist_ok=True)
        level = logging.DEBUG if verbose else logging.INFO
        self.logger.setLevel(level)
        self.logger.handlers.clear()
        self.logger.propagate = False

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S"
        )

        file_handler = RotatingFileHandler(
            self.config.log_file,
            maxBytes=self.config.log_max_bytes,
            backupCount=self.config.log_backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)
        self.logger.addHandler(stream_handler)

    def handle_signal(self, signum: int, _frame) -> None:
        try:
            signal_name = signal.Signals(signum).name
        except ValueError:
            signal_name = str(signum)
        self.logger.warning("received signal=%s, shutting down", signal_name)
        self.running = False

    def is_process_alive(self, pid: int) -> bool:
        if pid <= 0:
            return False
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True

    def read_pid_file(self) -> Optional[int]:
        try:
            content = self.config.pid_file.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            return None
        except Exception:
            return None

        if not content:
            return None

        try:
            return int(content.splitlines()[0].strip())
        except ValueError:
            return None

    def acquire_pid_lock(self) -> None:
        self.config.pid_file.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.config.pid_file, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            if exc.errno in (errno.EACCES, errno.EAGAIN):
                existing_pid = self.read_pid_file()
                if existing_pid and self.is_process_alive(existing_pid):
                    raise AlreadyRunningError(f"daemon already running pid={existing_pid}") from exc
                raise AlreadyRunningError("daemon already running (pid file locked)") from exc
            raise

        payload = (
            f"{os.getpid()}\n"
            f"email={self.config.email}\n"
            f"log_file={self.config.log_file}\n"
            f"started_at={time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        os.ftruncate(fd, 0)
        os.write(fd, payload.encode("utf-8"))
        os.fsync(fd)
        self._pid_fd = fd
        atexit.register(self.release_pid_lock)

    def release_pid_lock(self) -> None:
        if self._pid_fd is None:
            return
        try:
            try:
                os.ftruncate(self._pid_fd, 0)
            except OSError:
                pass
            try:
                fcntl.flock(self._pid_fd, fcntl.LOCK_UN)
            except OSError:
                pass
            try:
                os.close(self._pid_fd)
            except OSError:
                pass
        finally:
            self._pid_fd = None
            try:
                self.config.pid_file.unlink(missing_ok=True)
            except Exception:
                pass

    def load_password(self) -> str:
        if not self.config.password_file.exists():
            raise FileNotFoundError(f"password file not found: {self.config.password_file}")
        password = "".join(self.config.password_file.read_text(encoding="utf-8").split())
        if len(password) != 16:
            raise ValueError(f"app password length invalid: {len(password)}")
        return password

    def connect(self):
        password = self.load_password()
        mail = imaplib.IMAP4_SSL(
            self.config.imap_server,
            self.config.imap_port,
            ssl_context=ssl.create_default_context(),
        )
        mail.login(self.config.email, password)
        result, data = mail.select("INBOX")
        if result != "OK":
            raise RuntimeError(f"select INBOX failed: {result} {data}")
        count = int(data[0]) if data else 0
        self.stats.total_connections += 1
        return mail, count

    def read_response(self, sock, timeout: Optional[float] = None) -> str:
        sock.settimeout(timeout or self.config.socket_timeout_seconds)
        try:
            data = sock.recv(4096)
            return data.decode("utf-8", errors="ignore").strip() if data else ""
        except socket.timeout:
            return ""
        finally:
            try:
                sock.settimeout(None)
            except Exception:
                pass

    def start_idle(self, mail):
        tag = mail._new_tag()
        mail.socket().sendall(f"{tag} IDLE\r\n".encode("utf-8"))
        response = self.read_response(mail.socket())
        if "+" not in response:
            raise IdleRejectedError(f"IDLE rejected: {response}")
        return time.time()

    def stop_idle(self, mail) -> None:
        try:
            mail.socket().sendall(b"DONE\r\n")
            self.read_response(mail.socket(), timeout=2)
        except Exception:
            pass

    def parse_exists(self, response: str) -> Optional[int]:
        import re

        match = re.search(r"(\d+) EXISTS", response)
        if not match:
            return None
        return int(match.group(1))

    def build_received_event(
        self, *, exists_count: int, previous_count: int
    ) -> MailMessageReceivedEvent:
        return MailMessageReceivedEvent.from_exists_counts(
            provider="gmail-imap-idle",
            mailbox=self.config.email,
            exists_count=exists_count,
            previous_exists_count=previous_count,
        )

    def maybe_log_heartbeat(self, last_count: int, idle_started: float) -> None:
        now_ts = time.time()
        if now_ts - self.stats.last_heartbeat_at < self.config.heartbeat_interval_seconds:
            return
        self.stats.last_heartbeat_at = now_ts
        self.logger.info(
            "heartbeat pid=%s inbox_count=%s total_connections=%s total_mail_events=%s idle_seconds=%s",
            os.getpid(),
            last_count,
            self.stats.total_connections,
            self.stats.total_mail_events,
            int(now_ts - idle_started),
        )

    def monitor_once(self) -> None:
        mail = None
        try:
            mail, last_count = self.connect()
            self.logger.info("connected email=%s inbox_count=%s", self.config.email, last_count)

            capability_data = mail.capability()[1]
            caps = (
                b" ".join(capability_data).decode("utf-8", errors="ignore")
                if capability_data
                else ""
            )
            if "IDLE" not in caps.upper():
                raise RuntimeError(f"server does not support IDLE: {caps}")
            self.logger.info("server capability includes IDLE")

            idle_started = self.start_idle(mail)
            self.stats.last_heartbeat_at = 0.0
            self.logger.info("idle started")

            while self.running:
                if time.time() - idle_started >= self.config.idle_refresh_seconds:
                    self.logger.info("refreshing idle session")
                    self.stop_idle(mail)
                    idle_started = self.start_idle(mail)
                    self.logger.info("idle refreshed")

                self.maybe_log_heartbeat(last_count, idle_started)

                mail.socket().settimeout(1.0)
                try:
                    data = mail.socket().recv(4096)
                    if not data:
                        raise ConnectionError("socket closed by server")
                    response = data.decode("utf-8", errors="ignore").strip()
                    if not response:
                        continue

                    if "EXISTS" in response:
                        new_count = self.parse_exists(response)
                        if new_count is None:
                            self.logger.warning("exists_response_unparsed raw=%s", response)
                            continue
                        if new_count > last_count:
                            self.stats.total_mail_events += 1
                            event = self.build_received_event(
                                exists_count=new_count,
                                previous_count=last_count,
                            )
                            self.logger.info("new_mail event=%s", event.to_dict())
                        else:
                            self.logger.info(
                                "exists_update count=%s previous_count=%s", new_count, last_count
                            )
                        last_count = new_count
                    elif "RECENT" in response:
                        self.logger.info("recent_update raw=%s", response)
                    elif "EXPUNGE" in response:
                        self.logger.info("expunge_update raw=%s", response)
                    elif response.startswith("* OK"):
                        self.logger.debug("server_ok raw=%s", response)
                    else:
                        self.logger.info("server_update raw=%s", response)
                except socket.timeout:
                    pass
                finally:
                    try:
                        mail.socket().settimeout(None)
                    except Exception:
                        pass
        finally:
            if mail is not None:
                self.stop_idle(mail)
                try:
                    mail.logout()
                except Exception:
                    pass
                self.logger.info("connection closed")

    def compute_reconnect_delay(self, attempt: int) -> int:
        delay = self.config.reconnect_base_delay_seconds * (2 ** max(0, attempt - 1))
        return min(delay, self.config.reconnect_max_delay_seconds)

    def run_forever(self) -> int:
        self.acquire_pid_lock()
        self.logger.info(
            "mail-listener starting pid=%s email=%s pid_file=%s log_file=%s",
            os.getpid(),
            self.config.email,
            self.config.pid_file,
            self.config.log_file,
        )

        while self.running:
            try:
                self.monitor_once()
                self.stats.reconnect_attempt = 0
            except AlreadyRunningError:
                raise
            except Exception as exc:
                self.stats.reconnect_attempt += 1
                delay = self.compute_reconnect_delay(self.stats.reconnect_attempt)
                self.logger.exception(
                    "listener_error attempt=%s delay=%ss detail=%s",
                    self.stats.reconnect_attempt,
                    delay,
                    exc,
                )
                if not self.running:
                    break
                self.logger.warning("reconnecting in %ss", delay)
                time.sleep(delay)

        self.logger.info("mail-listener stopped")
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="mail-listener Gmail IMAP IDLE daemon (foreground; use a supervisor if needed)"
    )
    parser.add_argument("--verbose", action="store_true", help="enable debug logging")
    parser.add_argument("--check", action="store_true", help="validate secret file and exit")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    daemon = GmailIdleDaemon()
    daemon.configure_logging(verbose=args.verbose)

    signal.signal(signal.SIGINT, daemon.handle_signal)
    signal.signal(signal.SIGTERM, daemon.handle_signal)

    if args.check:
        daemon.load_password()
        daemon.logger.info("check_ok password_file=%s", daemon.config.password_file)
        return 0

    return daemon.run_forever()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AlreadyRunningError as exc:
        logging.basicConfig(level=logging.ERROR)
        logging.getLogger("mail_listener.gmail_idle").error("%s", exc)
        raise SystemExit(1)
