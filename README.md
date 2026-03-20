# mail-ingress-kit

A skill-first, adapter-friendly scaffold for **mail ingress**, **mailbox listening**, and **mail event delivery**.

This repository is intentionally positioned as a **general mail ingress foundation**, not a Gmail-only project. The goal is to support multiple mailbox providers and ingestion patterns over time, while remaining friendly to both **human operators** and **agent runtimes** such as **OpenClaw**, **Codex**, and **Cloud Code**.

## Why this exists

Many automation stacks need a clean way to:

- watch one or more mailboxes
- normalize incoming messages into events
- route events into downstream skills, agents, or workflows
- keep provider-specific code isolated behind adapters

This scaffold creates the boundaries for that work without prematurely locking the project into one provider.

## Current positioning

- **Project type:** foundation / scaffold
- **Primary concern:** mailbox listener + mail ingress event pipeline
- **Design style:** skill-first, adapter-oriented, agent-compatible
- **Current known adapter note:** Gmail via IMAP IDLE has already been validated as a promising first adapter, but it is treated here as an implementation note, not as the product identity

## Repository goals

- Keep the **core** reusable and provider-neutral
- Make **skills/** easy to split into an independent repository later
- Support both **human-facing documentation** and **agent-facing operating instructions**
- Keep source code and runtime environment separate

## Initial structure

```text
mail-ingress-kit/
├─ AGENTS.md
├─ LICENSE
├─ README.md
├─ README.zh-CN.md
├─ pyproject.toml
├─ .gitignore
├─ docs/
│  └─ architecture.md
├─ examples/
│  └─ sample-event.json
├─ scripts/
│  └─ bootstrap.sh
├─ skills/
│  └─ README.md
└─ src/
   └─ mail_ingress_kit/
      ├─ __init__.py
      ├─ adapters/
      │  └─ __init__.py
      ├─ core/
      │  └─ __init__.py
      ├─ events/
      │  └─ __init__.py
      └─ skills/
         └─ __init__.py
```

## Usage direction

This repository is not yet a full implementation. It is a starting point for:

1. defining a provider-neutral event model
2. adding mailbox adapters
3. wiring agent-consumable skills and command surfaces
4. documenting safe local and CI usage

## Local development

Recommended pattern:

- keep source code in this repository
- create runtime environments outside committed source where practical, or in ignored local directories such as `.venv/`
- avoid storing secrets in tracked files

Example:

```bash
cd mail-ingress-kit
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Near-term roadmap

- define canonical mail event schema
- add first adapter contract and lifecycle hooks
- document Gmail IMAP IDLE as the first validated adapter note
- add skill packaging conventions for standalone publishing
- add tests and CI once implementation starts

## Naming candidates

If the final repository name is still open, some reasonable options are:

- `mail-ingress-kit`
- `mail-event-bridge`
- `mailbox-ingress`
- `mail-listener-core`
- `mail-adapter-kit`

## License

Apache License 2.0.
