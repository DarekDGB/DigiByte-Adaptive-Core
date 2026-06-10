# Adaptive Core v3 AdamantineOS Integration

Author attribution: **DarekDGB**
Repository: `DigiByte-Adaptive-Core`
Status: AdamantineOS advisory evidence exporter documentation
Adaptive Core version boundary: `v3.0.0` remains unchanged
AdamantineOS receiver boundary: `DigiByte-Adamantine-Wallet-OS` Milestone 16E

---

## 1. Purpose

This document describes the Adaptive Core v3 AdamantineOS-facing exporter added during AdamantineOS Milestone 16E hardening.

Adaptive Core remains advisory evidence only.

It does not approve execution.
It does not sign.
It does not broadcast.
It does not override Shield, WSQK, Q-ID, AI Gateway, replay, wallet-policy, or human-gate decisions.
It does not create final authority outside AdamantineOS.

---

## 2. Exporter surface

Accepted external surface:

```text
adaptive_core.v3.integration.adamantine
```

Public symbols:

```text
ADAMANTINE_ADVISORY_EVIDENCE_VERSION
build_adamantine_advisory_evidence_v1(...)
validate_adamantine_advisory_evidence_v1(...)
```

The exporter creates an AdamantineOS-consumable evidence object with:

```text
ac_iface_version = adaptive_core_oracle_v3
```

---

## 3. Required evidence fields

```text
context_hash
issued_at
expires_at
generated_at
overall_score
signals
oracle_version
external_source_id
```

The `context_hash` must be lowercase 64-character hex.

When `now` is supplied to the builder or validator, the evidence must satisfy:

```text
issued_at <= now <= expires_at
generated_at <= now
```

---

## 4. Forbidden authority fields

The exporter fails closed if the payload contains authority-bearing fields such as:

```text
allow
approve
approved
authority
authorization
bypass
final_approval
grant_execution
handoff_allowed
override
```

This applies recursively, including nested signal payloads.

---

## 5. Shared proof vector

Adaptive Core includes this deterministic fixture:

```text
tests/fixtures/adamantine/adaptive_core_adamantine_advisory_evidence_v1.json
```

The exporter test proves that `build_adamantine_advisory_evidence_v1(...)` emits this exact fixture.

AdamantineOS uses the matching fixture on the receiving side:

```text
tests/fixtures/adaptive_core_external_baseline/adaptive_core_adamantine_advisory_evidence_v1.json
```

This provides a two-sided deterministic proof vector without adding final authority to Adaptive Core.

---

## 6. Verification

```text
PYTHONPATH=src pytest -q
```

Expected result:

```text
Full suite passes.
Required coverage remains 100%.
Adaptive Core remains v3.0.0.
No Adaptive Core tag is created.
```
