# AGENTS.md

Agent-oriented operating notes for `mail-ingress-kit`.

## Project intent

This repository is a **general mail ingress foundation** for human users and agent users.
Do not narrow the project identity to Gmail unless a maintainer explicitly decides to do so.
Gmail IMAP IDLE may be referenced as the **current validated adapter note**, not as the repository identity.

## Working principles

- Prefer provider-neutral abstractions in `src/mail_ingress_kit/core/` and `src/mail_ingress_kit/events/`.
- Keep provider-specific logic inside adapter boundaries.
- Keep `skills/` organized so it can be split into its own repository later with minimal restructuring.
- Prefer small, reviewable scaffolding changes before heavy implementation.
- Do not commit secrets, credentials, mailbox samples containing private content, or local environment files.

## Human + agent audience

When adding documentation:

- keep `README.md` as the main English entrypoint
- keep `README.zh-CN.md` aligned for Chinese readers
- keep agent instructions concise, operational, and English-first

## Suggested contribution path

1. Define the canonical mail event shape.
2. Define adapter interfaces and lifecycle hooks.
3. Add a first adapter behind those interfaces.
4. Add skills that consume normalized events.
5. Add tests, fixtures, and CI once the contracts stabilize.

## Skills boundary

Treat `skills/` as a future standalone publishable unit.
If you add files there, avoid tight coupling to repository-internal paths unless documented.

## Safe defaults

- Use ignored local runtime folders such as `.venv/`, `.cache/`, or `tmp/` when needed.
- Keep examples synthetic and scrubbed.
- Prefer Apache-2.0-compatible additions.
