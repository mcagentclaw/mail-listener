# mail-listener

[![CI](https://github.com/mcagentclaw/mail-listener/actions/workflows/ci.yml/badge.svg)](https://github.com/mcagentclaw/mail-listener/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](pyproject.toml)

> Turn mailbox activity into durable events for agents, workflows, and automation.

`mail-listener` is an open-source foundation for teams that want to treat email as a real event source instead of a messy side channel.

It helps you answer a deceptively hard question:

**How do you keep a mailbox listener running reliably, detect new mail quickly, and hand that signal to agents or workflows without building everything from scratch?**

Today, the repository ships with a validated **Gmail IMAP IDLE** implementation as the current adapter. The product direction is intentionally broader: `mail-listener` is meant to become a **provider-neutral mail listener layer** that can support more mailbox providers over time.

## Why this exists

Email is still one of the main ingress channels in real systems.

That is where many critical signals first appear:

- account verification and security notices
- customer replies and shared inbox activity
- invoices, receipts, and operational alerts
- approval requests and platform notifications
- workflow triggers from external systems

The problem is that mailbox handling is usually built in the worst possible order:

- first as throwaway scripts
- then as polling jobs
- then as a fragile “temporary” daemon
- then as a provider-specific tangle no one wants to touch

By the time a team wants to connect email to an agent or automation stack, the foundation is already brittle.

`mail-listener` focuses on fixing that **first mile**.

It is not trying to be a giant workflow platform. It is trying to do one job well:

> keep a mailbox listener alive, detect new mail with low latency, and emit a stable event boundary that other systems can trust.

## What pain it solves

`mail-listener` is for teams that are tired of one or more of these problems:

- polling-based mailbox checks that are slow, noisy, and wasteful
- mailbox listeners that die quietly after a reconnect or host restart
- provider-specific scripts that cannot be reused elsewhere
- agent systems that can *read* mail but lack a durable inbound event layer
- automation projects where transport concerns and business logic are tangled together

## Typical use cases

You may want `mail-listener` if you need to:

- monitor a shared inbox for new customer replies
- detect verification emails from external platforms
- watch for alerts, receipts, invoices, or notifications
- trigger internal workflows when a mailbox changes
- feed normalized mail events into bots, skills, task systems, or workflow engines
- run mailbox listeners continuously on a laptop, workstation, server, or managed agent host

## Why this matters for OpenClaw

`mail-listener` fits naturally into **OpenClaw-style agent environments**.

In many agent systems, the hard part is not only reasoning about incoming information — it is getting that information into the system in a clean, durable, and automatable way.

That is where `mail-listener` fits.

In an OpenClaw workflow, it can provide the missing boundary between the outside world and the agent layer:

1. keep the mailbox listener running over time
2. detect new-mail events with low latency
3. normalize provider-specific behavior into a clean event model
4. hand the event to OpenClaw agents, skills, routing, or downstream automation

This makes it useful for scenarios like:

- triggering an OpenClaw agent when a new operational email arrives
- turning incoming email into structured events before business logic runs
- feeding mailbox events into skills or orchestration pipelines
- separating **mail ingress** from **reasoning, routing, and action**

A simple way to think about the boundary is:

- `mail-listener` handles **mail ingress**
- OpenClaw handles **reasoning, routing, skills, and action**

That separation is intentional.

## mail-listener vs. OpenClaw cron jobs

`mail-listener` and OpenClaw cron jobs solve different problems.

### Use `mail-listener` when

- you need to react to **mailbox changes**
- you want **event-driven** behavior instead of scheduled polling
- latency matters and you want to notice new mail soon after it arrives
- email is the trigger, and agents or workflows should run **after** the mail event happens

### Use OpenClaw cron when

- you need something to run on a **schedule**
- the trigger is time-based rather than mailbox-based
- you want reminders, periodic checks, daily summaries, or recurring maintenance tasks
- you are fine with a job running every N minutes / hours / days regardless of whether new mail arrived

### Common pattern

In OpenClaw-style systems, the two can work together:

- `mail-listener` detects the new message
- OpenClaw agents or workflows decide what to do next
- cron handles follow-up jobs, retries, summaries, deadlines, or scheduled maintenance around that workflow

A simple rule of thumb:

- **new mail arrived** → `mail-listener`
- **run this at 9:00 every day** → OpenClaw cron

## Current status

The current repository packages the already-validated **Gmail IMAP IDLE** implementation as the **current adapter**.

Included today:

- Gmail IMAP IDLE listener
- long-running foreground daemon suitable for supervisor / launchd management
- automatic reconnect with exponential backoff
- rotating logs
- PID lock file to avoid duplicate starts
- `--check` secret validation
- a normalized `mail.message.received` event shape for the current adapter
- CI quality gates for formatting, linting, and smoke tests

Not included yet:

- OAuth-based mailbox auth flow
- mail body parsing
- attachment extraction
- downstream workflow orchestration
- production-ready adapters beyond the current Gmail implementation
- full skill implementations

So the project is already useful as a **mail listener foundation**, but it is not pretending to be a complete mail automation platform yet.

## Who this is for

`mail-listener` is for teams that need:

- developers building mailbox-driven automation
- teams wiring email into agent workflows
- OpenClaw users who want a durable mail-ingress layer
- operators who need a listener that can actually stay alive in the real world

## Who this is not for

`mail-listener` is probably not the right project if you need:

- a full helpdesk product
- a complete email parser and processor out of the box
- an all-in-one workflow engine
- a polished multi-provider platform today

The current goal is narrower and more foundational.

## Quick start

```bash
cd mail-listener
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Validate the current mailbox secret configuration:

```bash
mail-listener --check
```

Run the current Gmail IMAP IDLE listener:

```bash
mail-listener
```

Verbose mode:

```bash
mail-listener --verbose
```

## Repository layout

```text
mail-listener/
├─ .github/workflows/ci.yml
├─ AGENTS.md
├─ LICENSE
├─ README.md
├─ README.zh-CN.md
├─ deploy/
├─ docs/
├─ examples/
├─ scripts/
├─ skills/
├─ src/
└─ tests/
```

Key structure decisions:

- `src/` keeps the main source tree provider-neutral
- `adapters/` isolates provider-specific listener logic
- `events/` defines the event boundary downstream systems consume
- `skills/` stays top-level so it can later be split into a standalone skill repository if needed
- `AGENTS.md` is written for coding agents and maintainers, not end users

## Quality gates

The same gates run locally and in CI:

```bash
ruff format --check .
ruff check .
pytest
```

## Current event shape

The current adapter emits a normalized event payload like this:

```json
{
  "event_type": "mail.message.received",
  "provider": "gmail-imap-idle",
  "mailbox": "listener@example.test",
  "exists_count": 42,
  "previous_exists_count": 41,
  "received_at": "2026-03-20T04:00:00+00:00"
}
```

## macOS runtime operations

For the current Gmail IMAP IDLE implementation, the repository includes:

- `scripts/gmail_idle_ctl.sh` for start / stop / status / logs
- `deploy/com.mail-listener.gmail-imap-idle.plist` as a `launchd` template

Example:

```bash
./scripts/gmail_idle_ctl.sh check
./scripts/gmail_idle_ctl.sh start
./scripts/gmail_idle_ctl.sh status
./scripts/gmail_idle_ctl.sh logs
```

## Roadmap direction

The long-term direction is not “Gmail only.”

The intended shape is:

- one reusable mail-listener core
- multiple provider adapters
- stable mail-event contracts
- optional skills and automation packages on top

Gmail IMAP IDLE is simply the first validated adapter on that path.

## License

Apache License 2.0.
