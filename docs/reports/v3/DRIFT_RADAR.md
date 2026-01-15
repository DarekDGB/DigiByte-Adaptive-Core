# DRIFT_RADAR (v3)

## Purpose

Drift Radar detects **contract drift** between:
- expected layer contracts (explicit inputs)
- observed patterns / evidence (from the v3 pipeline context)

Implementation:
- `adaptive_core.v3.drift`
- optional graph output: `adaptive_core.v3.graph`

Drift Radar is **opt-in**: no contracts → no drift analysis.

---

## Inputs

- `drift_contracts: list[LayerContract] | None`
- `include_drift_graph: bool`

Contracts are explicit, versioned expectations for target layers.

---

## Outputs

When enabled, Drift Radar contributes deterministic findings to the report, e.g.:

- missing expected signals
- incompatible schema changes
- unexpected behavior indicators
- contract version mismatches

When `include_drift_graph=True`, the report may include a DOT graph string that
represents contract relationships or drift edges.

---

## Guardrails

1. **Explicit contracts only**: Drift Radar must not infer contracts from thin air.
2. **Deterministic**: drift results must be stable for the same inputs.
3. **Fail-closed for malformed contracts**: invalid contract objects must raise.
4. **No auto-remediation**: drift is reporting only.

---

## Recommended usage

- Provide drift contracts for layers you intend to upgrade.
- Turn on `include_drift_graph` only for human review workflows (DOT can be large).
- Store drift graphs as review artifacts (PR attachments), not as runtime requirements.

---

## Future evolution

- Contract schemas may expand, but must remain strict and versioned.
- Any new drift reason IDs must be added to `ReasonId` and tested.
