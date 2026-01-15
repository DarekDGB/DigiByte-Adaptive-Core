# Adaptive Core v2 — Legacy Learning Engine (Overview)

Adaptive Core v2 is the historical “learning engine” implementation that existed before the v3 Upgrade Oracle work.

It includes v2 concepts such as:

- immune report generation
- threat packet ingestion
- heuristic learning / reinforcement-style update logic
- memory stores and sinks

## Important: v2 vs v3

- v2 is **legacy** and may remain in the repository for compatibility and historical context.
- v3 is the **current** architecture direction for the shield’s upgrade oracle.

v3 is intentionally stricter and more protocol-like:

- deterministic outputs
- strict canonicalization
- explicit reason IDs
- guardrails registry
- no execution authority

## v2 Docs

Legacy report docs are here:

- `reports/immune-report-schema.md`
- `reports/qri-scoring.md`
- `reports/reinforcement-learning-rules.md`
