# Adaptive Core v3 — Proposals Mailbox

This folder is the canonical inbox for **upgrade proposals** submitted to Adaptive Core.

## How proposals arrive

- External systems (e.g. AdamantineOS) submit a proposal via **GitHub Pull Request**
- The proposal JSON lives under: `proposals/inbox/`
- CI can validate:
  - schema
  - deterministic fields
  - required reason IDs / guardrails
  - hash / canonical form (later)

## Folders

- `proposals/schema/` — JSON Schemas that proposals must satisfy
- `proposals/template/` — templates for proposal authors
- `proposals/inbox/` — PRs add proposal files here (created later)

## Status

This is a mailbox only. Execution/wiring happens inside AdamantineOS and the adapter layer.
