# Adaptive Core v3 AdamantineOS Integration

Author attribution: **DarekDGB**
Repository: `DigiByte-Adaptive-Core`
Status: Normative advisory exporter and Shield v4 compatibility documentation
Adaptive Core version boundary: `v3.0.0` remains unchanged
AdamantineOS receiver boundary: `DigiByte-AdamantineOS` verify-only Shield boundary

---

## 1. Purpose

This document defines the Adaptive Core v3 AdamantineOS-facing exporter and its Shield v4 compatibility boundary.

Adaptive Core remains advisory evidence only.

It does not approve execution.
It does not sign.
It does not broadcast.
It does not verify Shield signatures or interpret Shield cryptographic evidence.
It cannot approve, override, downgrade, bypass, or rescue Shield, Q-ID, AI Gateway, replay, wallet-policy, or human-gate decisions.
AdamantineOS remains the authoritative, fail-closed final policy and execution boundary.

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

## 3. V1 evidence shape

Required root fields:

```text
ac_iface_version
context_hash
issued_at
expires_at
generated_at
overall_score
signals
```

Optional source metadata:

```text
oracle_version
external_source_id
```

When either optional field is absent, the normalized output contains that field with `null`. This is existing V1 behavior and is not silently reinterpreted as proof of source identity.

Every `signals[]` object has exactly these required fields:

```text
source
severity
reason_ids
```

`signals` must be a non-empty sequence. Each `reason_ids` value must also be a non-empty sequence, and every reason ID must be a non-empty string. Nested objects are not accepted.

`issued_at`, `expires_at`, `generated_at`, `overall_score`, signal `severity`, and supplied `now` values must be integers; booleans are rejected. `overall_score` and `severity` must be in the inclusive range 0 through 100. `generated_at` must be positive, and `expires_at` must be greater than or equal to `issued_at`.

If `oracle_version` or `external_source_id` is present, it must normalize to a non-empty stripped string.

Unknown root or signal fields fail closed with `AC_V3_REPORT_INVALID`.

The `context_hash` must be lowercase 64-character hex.

When `now` is supplied to the builder or validator, the evidence must satisfy:

```text
issued_at <= now <= expires_at
generated_at <= now
```

---

## 4. Closed authority and Shield fields

The exact V1 shape has no authority, signature, key, algorithm, profile, policy, verdict, or decision field. Any such extra field fails closed, including case variants. Examples include:

```text
authority
bypass
decision
final_approval
handoff_allowed
override
shield_receipt
signature
algorithm
standard_profile
key_role
```

The exporter normalizes accepted scalar and list data only. It does not recursively accept arbitrary nested signal metadata.

---

## 5. Shield v4 cryptographic separation

Adaptive Core has no Shield trust registry, Shield key role, signature backend, or OQS dependency. It does not inspect or verify Shield signature bundles.

The Shield verifier-required policy remains:

```text
classical-ed25519 + ml-dsa
```

Optional `fn-dsa` evidence uses Falcon-1024 under `fips206-draft-falcon1024-v1`. It is optional draft-profile evidence, not final FIPS 206 proof. Adaptive telemetry cannot make FN-DSA required or use it to replace, rescue, override, or downgrade required verification.

The local report-envelope values `classical_signature` and `pqc_signature` use `ABSENT`, `PRESENT`, or `UNSUPPORTED`. They are caller-supplied report metadata, not verified Shield proof.

Q-ID identity keys and Shield decision-evidence keys remain separate. Cryptographic evidence proves Shield evidence; it grants no execution authority. AdamantineOS independently verifies Shield evidence under verifier-controlled policy and remains final.

---

## 6. Shared proof vector

Adaptive Core includes this deterministic fixture:

```text
tests/fixtures/adamantine/adaptive_core_adamantine_advisory_evidence_v1.json
```

The exporter test proves that `build_adamantine_advisory_evidence_v1(...)` emits this exact fixture.

Fixture SHA-256:

```text
5b7d99ec53bfccca70b28c7bc286f388c966eb3ef33f1c1dac20b7eafac4b43d
```

AdamantineOS uses the matching fixture on the receiving side:

```text
tests/fixtures/adaptive_core_external_baseline/adaptive_core_adamantine_advisory_evidence_v1.json
```

This provides a two-sided deterministic proof vector without adding final authority to Adaptive Core.

---

## 7. Verification

```text
PYTHONPATH=src pytest -q
```

Expected result:

```text
260 passed.
0 skipped, failures, or errors.
1,505 of 1,505 statements covered.
Required statement coverage remains 100%.
Adaptive Core remains v3.0.0.
No Adaptive Core tag is created.
No Shield cryptographic verification is added.
```
