# Adaptive Core v3 — Upgrade Oracle (Overview)

Adaptive Core v3 is the **Upgrade Oracle** for the DigiByte Quantum Shield.

It is intentionally designed as:

- **Read-only / advisory**
- **Deterministic**
- **Fail-closed**
- **Human-reviewed**

## What v3 does

v3 consumes **strict, canonicalized, v3-shaped observations** and produces:

- deterministic evidence counters (hot-window)
- deterministic findings
- deterministic reports (JSON + Markdown)
- a deterministic integrity envelope (hash + signature status)

## What v3 does NOT do

v3 does not:

- execute transactions
- change wallet or node state
- hold cryptographic keys
- auto-apply patches or upgrades
- silently accept malformed inputs
- infer or guess missing data

## Current v3 components (as implemented)

- Canonicalization: `adaptive_core.v3.canonicalize`
- Evidence window: `adaptive_core.v3.evidence_store`
- Findings & analysis: `adaptive_core.v3.analyze`, `adaptive_core.v3.findings`
- Drift detection: `adaptive_core.v3.drift`
- Guardrails registry: `adaptive_core.v3.guardrails.registry`
- Report generation: `adaptive_core.v3.report_builder`
- Integrity envelope: `adaptive_core.v3.envelope`
- Pipeline orchestration: `adaptive_core.v3.pipeline`
- Cross-node summary (privacy-preserving): `adaptive_core.v3.node_summary`

## Guardrails: single source of truth

Adaptive Core v3 enforces a **machine-validated guardrails registry**.

- Unknown guardrail IDs are rejected (**fail-closed**).
- Guardrails are referenced by ID in findings and reports.
- Guardrails define **limits**, not actions.

See: [GUARDRAILS.md](GUARDRAILS.md)
