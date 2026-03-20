# Architecture Notes

## Intent

This project is structured around a provider-neutral mail ingress pipeline.

## Boundaries

### Core

`src/mail_ingress_kit/core/`

Contains interfaces, orchestration primitives, and lifecycle concepts that should remain independent from any single provider.

### Events

`src/mail_ingress_kit/events/`

Contains normalized event models and translation targets for downstream automation.

### Adapters

`src/mail_ingress_kit/adapters/`

Contains provider-specific connectors such as IMAP, Gmail, or future API/webhook-based integrations.

### Skills

`skills/`

Reserved for skill packages, prompts, descriptors, and agent-facing integration assets. The directory is intentionally top-level so it can be split into an independent repository later if needed.

## Current implementation note

A Gmail IMAP IDLE path has already been validated conceptually and should be documented as the first working adapter candidate. However, the repository should continue to describe itself as mail-ingress-oriented rather than Gmail-specific.

## TODO

- define canonical event schema
- define adapter contract and capability matrix
- decide whether skills ship from this repository or a future companion repository
- add tests for normalization and adapter compliance
