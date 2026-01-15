# Adaptive Core v3 — CONTRACT (Normative)

**Status:** Normative • Contract-Locking Document  
**Scope:** `adaptive_core.v3.*` (read-only upgrade oracle)

This document is **normative**. If code or any other documentation conflicts with this file, **this file wins**.

---

## 1. Purpose

Adaptive Core v3 (“ACv3”) is the **Upgrade Oracle** for the DigiByte Quantum Shield.

It ingests **strict, canonicalized, v3-shaped observations** and produces **deterministic advisory outputs**:

- evidence counters (bounded hot window)
- findings (including optional drift findings when explicit contracts are provided)
- upgrade reports (canonical JSON + stable Markdown)
- integrity envelope (deterministic hash + explicit signature status)

ACv3 is designed to support **human-reviewed decisions** and **downstream enforcement** by other layers.

---

## 2. Authority Model (Non-Authority Invariant)

ACv3 is **read-only / advisory**.

ACv3 **MUST NOT**:
- execute transactions
- sign transactions
- hold private keys
- access seed phrases
- change wallet/node state
- auto-apply patches
- self-upgrade any software component
- write to disk implicitly
- perform network I/O implicitly

ACv3 **MAY**:
- validate inputs strictly (fail-closed)
- compute deterministic summaries and reports
- emit reason-coded errors on invalid inputs
- generate an integrity envelope with explicit signature status fields

---

## 3. Determinism Contract

ACv3 outputs MUST be deterministic given the same inputs.

Determinism requirements:
- Canonical JSON renderers MUST use stable ordering (sorted keys) and stable types.
- Hashing MUST be performed over canonical JSON only.
- No randomness, time-based variability, or hidden state may influence report outputs.
- Any optional feature must be explicitly enabled by parameters (no silent feature toggles).

If any input is invalid, ACv3 MUST fail with a **ReasonId** and MUST NOT silently guess or patch data.

---

## 4. Fail-Closed Input Contract

ACv3 MUST reject malformed inputs rather than attempting recovery via inference.

In particular:
- Missing required fields => error with `AC_V3_MISSING_FIELD`
- Type mismatches => error with `AC_V3_TYPE_INVALID`
- Non-canonical values => error with `AC_V3_NON_CANONICAL`
- Timestamp issues => error with `AC_V3_TIMESTAMP_INVALID`
- Invalid meta => error with `AC_V3_META_INVALID`
- Invalid event container => error with `AC_V3_INVALID_EVENT`

ACv3 MUST NOT:
- fill missing required fields
- normalize unknown shapes silently
- accept unknown guardrail IDs

---

## 5. Integrity Envelope Contract

ACv3 MUST produce an envelope with:
- `report_hash` = deterministic SHA-256 of the canonical JSON string
- explicit `classical_signature` status
- explicit `pqc_signature` status

Signature status values are limited to:
- `ABSENT`
- `PRESENT`
- `UNSUPPORTED`

No other values are permitted.

---

## 6. Components Bound to This Contract

This contract applies to the following v3 modules:

- Canonicalization: `adaptive_core.v3.canonicalize`
- Evidence store: `adaptive_core.v3.evidence_store`
- Findings: `adaptive_core.v3.analyze` + `adaptive_core.v3.findings`
- Drift Radar: `adaptive_core.v3.drift` (+ optional graph output via `adaptive_core.v3.graph`)
- Guardrails registry: `adaptive_core.v3.guardrails.registry`
- Report builder/renderers: `adaptive_core.v3.report_builder`
- Integrity envelope: `adaptive_core.v3.envelope`
- Pipeline orchestration: `adaptive_core.v3.pipeline`
- Cross-node summary (privacy-preserving): `adaptive_core.v3.node_summary`

---

## 7. Versioning Rules

- Any change that **relaxes** validation, changes canonicalization, or alters report structure is a **contract change**.
- Contract changes MUST be accompanied by:
  - explicit doc updates to this file
  - deterministic tests that lock the behavior (regression locks)

---

## 8. Out of Scope

The following are explicitly out of scope for ACv3:
- automated patch delivery
- auto-remediation
- autonomous governance
- wallet UX decisions
- network consensus modifications

ACv3 produces **advisory intelligence** only.
