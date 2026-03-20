# Architecture Notes

## Goal of this round

Extract the existing Gmail IMAP IDLE listener into a standalone repository named `mail-listener`, without expanding product scope.

## Layers

### `src/mail_listener/adapters/`

Provider-specific implementations live here.

Current implementation:

- `gmail/idle.py` — packaged version of the existing Gmail IMAP IDLE daemon

### `src/mail_listener/core/`

Small reusable runtime pieces used by adapters:

- config loading
- listener runtime stats
- process/runtime path conventions

### `src/mail_listener/events/`

Normalized event models emitted by the current adapter.

Current event model:

- `MailMessageReceivedEvent`

## Skill boundary

`skills/` remains top-level and intentionally light. It is preserved as a split-friendly boundary for future agent-facing packaging.

## Non-goals for this round

- no new provider adapters
- no mail parsing pipeline
- no workflow orchestration layer
- no feature expansion beyond the existing Gmail IMAP IDLE behavior

## Quality gate

The repository is expected to pass:

1. `ruff format --check .`
2. `ruff check .`
3. `pytest`
