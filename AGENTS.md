# AGENTS.md

Guidance for coding agents working on `mail-listener`.

This file is not user-facing product copy. Treat it as an internal engineering handoff document for agents contributing code to this repository.

## 1. Project context

`mail-listener` is a provider-extensible mailbox listener foundation.

The current repository scope is intentionally narrow:
- it packages the already-validated **Gmail IMAP IDLE** implementation
- it provides a clean event boundary for downstream systems
- it does **not** yet attempt to be a complete mail automation platform

When describing the project in code, docs, comments, or PR summaries:
- frame Gmail IMAP IDLE as the **current adapter / current implementation**
- do not imply that multi-provider support is already implemented
- do not imply that mail parsing, attachment handling, or workflow orchestration already exist

## 2. Tech stack

Core stack in this repository:

- Language: Python >= 3.9
- Packaging: `setuptools` via `pyproject.toml`
- CLI entrypoint: `mail-listener`
- Linting: `ruff`
- Testing: `pytest`
- CI: GitHub Actions
- Runtime model: long-running foreground process suitable for supervisor / launchd management

Current mailbox adapter:
- Gmail IMAP IDLE via Python standard-library style implementation

## 3. Code standards

These are the highest-priority rules.

### Architecture and boundaries
- Keep provider-specific logic under `src/mail_listener/adapters/`.
- Keep shared runtime/config logic under `src/mail_listener/core/`.
- Keep normalized event models under `src/mail_listener/events/`.
- Keep CLI behavior under `src/mail_listener/cli/`.
- Keep `skills/` as a top-level boundary that can later become an independent repository or package.

### Scope discipline
- Do not add new product capabilities unless explicitly requested.
- Prefer extraction, cleanup, structure, tests, docs, and operability improvements over feature expansion.
- Preserve the current feature boundary unless the user explicitly expands scope.

### Naming and style
- Follow existing Python naming conventions already present in the repo.
- Prefer small, focused modules over large mixed-responsibility files.
- Keep provider-neutral abstractions provider-neutral; do not leak Gmail-specific assumptions into shared core modules.
- Avoid unnecessary dependencies when the standard library is sufficient.

### Quality rules
- Do not commit secrets, mailbox content, tokens, or local runtime artifacts.
- Keep examples synthetic and safe for open-source publication.
- If you change package layout or CLI behavior, update docs and tests in the same change.

## 4. Folder structure

Use this as the source-of-truth placement guide:

- `src/mail_listener/adapters/` → provider-specific listener implementations
- `src/mail_listener/core/` → config, runtime primitives, shared operational models
- `src/mail_listener/events/` → normalized event contracts
- `src/mail_listener/cli/` → CLI entrypoints and argument handling
- `tests/` → smoke, unit, and regression tests
- `docs/` → human-facing architecture and supporting docs
- `skills/` → skill-facing boundary and future split point
- `scripts/` → operational helper scripts
- `deploy/` → deploy/supervisor templates such as `launchd` assets
- `examples/` → safe sample payloads and usage examples

## 5. Project constraints and pitfalls

These are the main traps to avoid.

- Do not market or document this as “Gmail only,” but also do not pretend non-Gmail adapters already exist.
- Do not move business workflow logic into the listener core.
- Do not couple downstream automation assumptions into adapter code.
- Do not store runtime state inside source directories if a runtime/cache directory is more appropriate.
- Do not weaken CI gates just to make a change pass.
- Do not silently change event shapes without updating examples, docs, and tests.

## 6. Workflow requirements

When doing non-trivial code changes, follow this workflow.

### Before coding
- Briefly state the intended change and the affected files/modules.
- Check whether the request is asking for refactor vs. new functionality.
- If the change might expand scope, pause and ask instead of assuming.

### While coding
- Keep edits consistent with the provider-neutral long-term direction.
- Update docs when behavior, structure, or commands change.
- Preserve open-source readiness: no machine-specific secrets, no private operational data.

### Before finishing
Run the local quality gates:

```bash
ruff format --check .
ruff check .
pytest
```

If any of these fail, do not present the work as complete.

## 7. Documentation expectations

This project serves both human users and agent users.

- `README.md` is the primary English user-facing document.
- `README.zh-CN.md` is the Chinese user-facing companion.
- `AGENTS.md` is for coding agents and maintainers.

When updating docs:
- keep the three documents aligned on project scope
- make README explain pain points, usage scenarios, and OpenClaw relevance clearly
- keep AGENTS.md operational and implementation-focused, not marketing-focused

## 8. CI expectations

The repository should remain green on:

```bash
ruff format --check .
ruff check .
pytest
```

If you add or move files that affect imports, commands, or packaging, update:
- tests
- GitHub Actions workflow
- relevant README / AGENTS sections

## 9. Current implementation boundary

As of now, this repository includes:
- Gmail IMAP IDLE listening
- reconnect / backoff behavior
- logging and PID/runtime handling
- supervisor-friendly execution
- normalized “mail received” event emission

As of now, this repository does not include:
- OAuth mailbox auth flows
- mail body parsing
- attachment extraction
- downstream workflow orchestration
- additional production adapters beyond Gmail IMAP IDLE

Protect this boundary unless the user explicitly asks to expand it.
