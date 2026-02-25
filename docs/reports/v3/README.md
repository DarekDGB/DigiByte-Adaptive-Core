# Adaptive Core v3 --- Upgrade Oracle (Overview)

Adaptive Core v3 is the **Upgrade Oracle** for the DigiByte Quantum
Shield.

It is intentionally designed as:

-   **Read-only / advisory**
-   **Deterministic**
-   **Fail-closed**
-   **Human-reviewed**
-   **No hidden authority**

> Adaptive Core v3 observes, summarizes, and reports.\
> It never executes, never modifies state, and never self-upgrades.

------------------------------------------------------------------------

## What v3 does

v3 consumes **strict, canonicalized, v3-shaped observations** and
produces:

-   Deterministic evidence counters (hot-window)
-   Deterministic findings
-   Deterministic reports (**JSON + Markdown**)
-   A deterministic integrity envelope (**context_hash + signature
    status**)

------------------------------------------------------------------------

## What v3 does NOT do

v3 does not:

-   Execute transactions
-   Change wallet or node state
-   Hold cryptographic keys
-   Auto-apply patches or upgrades
-   Silently accept malformed inputs
-   Infer or guess missing data

------------------------------------------------------------------------

## Current v3 components (as implemented)

All v3 implementation code lives under `src/adaptive_core/v3/`:

-   Canonicalization: `adaptive_core.v3.canonicalize`
-   Evidence window: `adaptive_core.v3.evidence_store`
-   Findings & analysis: `adaptive_core.v3.analyze`,
    `adaptive_core.v3.findings`
-   Drift detection: `adaptive_core.v3.drift`
-   Correlation & graph utilities: `adaptive_core.v3.correlation`,
    `adaptive_core.v3.graph`
-   Confidence scoring: `adaptive_core.v3.confidence`
-   Guardrails registry: `adaptive_core.v3.guardrails.registry`
-   Reason IDs: `adaptive_core.v3.reason_ids`
-   Report generation: `adaptive_core.v3.report_builder`
-   Integrity envelope: `adaptive_core.v3.envelope`,
    `adaptive_core.v3.context_hash`
-   Pipeline orchestration: `adaptive_core.v3.pipeline`
-   Cross-node summary (privacy-preserving):
    `adaptive_core.v3.node_summary`
-   Upgrade proposals (schema + validation helpers):
    `adaptive_core.v3.proposals`

------------------------------------------------------------------------

## Upgrade proposals mailbox (human-reviewed only)

Adaptive Core v3 maintains a structured proposals mailbox in the
repository root:

-   `proposals/schema/` --- authoritative JSON schemas
-   `proposals/template/` --- proposal templates
-   `proposals/inbox/` --- proposals submitted via Pull Request

Adaptive Core is **mailbox + validator**. It never applies upgrades
automatically.

See: [`proposals/README.md`](../../../proposals/README.md)

------------------------------------------------------------------------

## Guardrails: single source of truth

Adaptive Core v3 enforces a **machine-validated guardrails registry**.

-   Unknown guardrail IDs are rejected (**fail-closed**).
-   Guardrails are referenced by ID in findings and reports.
-   Guardrails define **limits**, not actions.

See: [GUARDRAILS.md](GUARDRAILS.md)
