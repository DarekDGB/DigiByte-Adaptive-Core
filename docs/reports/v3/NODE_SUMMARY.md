# NODE_SUMMARY (v3)

## Purpose

This document defines the **privacy-preserving cross-node summary** event used by v3.

Implementation: `adaptive_core.v3.node_summary`

The goal is to enable network-level aggregation without leaking raw telemetry.

---

## Event: NodeSummaryEventV3

Fields:

- `node_id: str` — pseudonymous identifier (no IPs, no secrets)
- `window_start: str` — ISO8601 timestamp, must end with `Z`
- `window_end: str` — ISO8601 timestamp, must end with `Z`
- `total_events: int` — aggregated count, must be >= 0
- `by_upstream_reason_id: dict[str, int]` — aggregated counts by reason id, values >= 0

---

## Canonicalization

Function: `canonicalize_node_summary(raw: Mapping[str, Any]) -> (NodeSummaryEventV3, context_hash)`

Rules:

- Missing required fields → `AC_V3_MISSING_FIELD`
- Type mismatch → `AC_V3_TYPE_INVALID`
- Timestamp missing trailing `Z` or invalid ISO → `AC_V3_TIMESTAMP_INVALID`
- Negative counters → `AC_V3_NON_CANONICAL`

The `context_hash` is computed from the canonical dict of the event.

---

## Privacy properties

- No raw events included.
- No packet payloads.
- Aggregation only.

---

## Integration notes

Node summaries are designed to be consumed by an aggregation layer (e.g., DQSN) and/or
used as part of broader evidence evaluation in Adaptive Core workflows.
