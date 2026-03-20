# skills/

This directory stays top-level on purpose.

## Why it still exists

`mail-listener` keeps a **skill-first boundary** even though this round only packages the current Gmail IMAP IDLE implementation.

That means `skills/` should remain easy to split into its own repository or package later.

## Current expectation

For now, keep this directory lightweight:

- contract notes
- prompts or templates
- packaging notes
- examples that do not depend on secrets

## Avoid

- hard wiring skills to deep repository internals
- embedding runtime secrets
- assuming features that are not implemented in the current repository

## Current implementation note

The current runtime implementation is the Gmail IMAP IDLE adapter under `src/mail_listener/adapters/gmail/`.
Future skills should consume normalized events rather than reaching directly into adapter internals when possible.
