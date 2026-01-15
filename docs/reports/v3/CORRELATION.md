# CORRELATION (v3)

## Purpose

Correlation groups related events into an incident-level view.

Implementation: `adaptive_core.v3.correlation`

Correlation is **off by default** unless explicitly enabled in a pipeline context,
because:

- incorrect correlation can create false narratives
- correlation often requires assumptions about time windows and identifiers
- strict determinism is easier when correlation is an explicit input/output step

---

## Inputs

Correlation operates on canonicalized v3 events:

- `correlation_id` is required in `ObservedEventV3`
- events may also carry `reason_id` and `meta` keys

---

## Outputs

Correlation yields deterministic groupings, e.g.:

- groups keyed by `correlation_id`
- group statistics (counts, max severity, involved layers)

Exact output shape is defined in code and is normative.

---

## Guardrails

1. **No implicit merging**: only `correlation_id` groups by default.
2. **Deterministic ordering**: stable sort/group operations.
3. **No time guessing**: windows must be explicit if used.
4. **Fail-closed**: invalid event shapes are rejected earlier (canonicalize step).

---

## Why off by default (policy)

- Many upstream producers (older layers) may generate low-quality or inconsistent correlation IDs.
- For security, itâs safer to emit **uncorrelated evidence** than to overfit.
- Humans can enable correlation for review workflows once upstream quality is confirmed.
