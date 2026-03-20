"""Console entry point for mail-listener."""

from __future__ import annotations

from mail_listener.adapters.gmail.idle import main as gmail_idle_main


def run() -> int:
    return gmail_idle_main()


if __name__ == "__main__":
    raise SystemExit(run())
