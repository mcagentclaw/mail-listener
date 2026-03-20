"""Gmail IMAP IDLE adapter."""

from .idle import GmailIdleDaemon, build_parser, main

__all__ = ["GmailIdleDaemon", "build_parser", "main"]
