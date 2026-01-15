# EVIDENCE_STORE (v3)

## Purpose

This document defines the **v3 Evidence Store**:

- a deterministic, bounded, in-memory hot-window store
- maintained counters for evidence aggregation
- no persistence by default (persistence is an explicit future step)

Implementation: `adaptive_core.v3.evidence_store.EvidenceStoreV3`

---

## Invariants

1. **Bounded memory**: window size is capped by `max_events`.
2. **Deterministic counters**: derived only from canonicalized events.
3. **Stable eviction**: FIFO eviction (oldest first) when full.
4. **No hidden persistence**: no disk I/O unless explicitly added in a future version.
5. **Fail-fast construction**: `max_events <= 0` raises.

---

## Data model

The store holds a deque of `CanonicalizeResult` entries, where each entry contains:

- `event: ObservedEventV3`
- `context_hash: str` (deterministic hash of the canonical event dict)

### Snapshot format

`EvidenceSnapshot` contains deterministic counters:

- `total_events`
- `by_source_layer`
- `by_event_type`
- `by_upstream_reason_id` (counts of `reason_id` when provided)

---

## Counter semantics

Counters increment on `add(item)`:

- `by_source_layer[event.source_layer] += 1`
- `by_event_type[event.event_type] += 1`
- `by_upstream_reason_id[event.reason_id] += 1` **only if reason_id is present**

On eviction, counters decrement, and keys with `<= 0` are removed.

---

## Deterministic ordering

- The hot-window iterates in **deque order**: oldest â newest.
- Snapshot dicts do not guarantee ordering (Python preserves insertion order, but consumers must not rely on it).
- Report renderers must sort keys if they need stable visual ordering.

---

## Failure modes

- Adding an item assumes the item is already canonicalized. Any canonicalization failures must happen earlier.
- Negative or zero `max_events` is rejected at init time.

---

## Future evolution (explicit)

Persistence and archival must be added as an opt-in layer with explicit guardrails:

- no implicit disk reads/writes
- no silent truncation beyond documented max size
- deterministic replay ordering (if replay is supported)
