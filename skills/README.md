# skills/

This directory is reserved for **agent-consumable skills** related to mail ingress.

## Why it is top-level

The project is being organized so that `skills/` can later become its own repository or distributable package with minimal reshaping.

That means:

- avoid unnecessary imports from deep repository internals
- document any required contracts explicitly
- keep prompts, metadata, examples, and packaging notes close to each skill

## Suggested future layout

```text
skills/
├─ README.md
├─ mail-listener/
│  ├─ SKILL.md
│  ├─ examples/
│  └─ references/
└─ mail-router/
   ├─ SKILL.md
   ├─ examples/
   └─ references/
```

## Packaging note

If this directory is split into a standalone repository later, keep the stable boundary at the event contract and adapter capability descriptions rather than at provider-specific implementation details.
