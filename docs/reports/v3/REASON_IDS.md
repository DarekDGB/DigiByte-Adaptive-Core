# Adaptive Core v3 — Reason IDs (Normative)

**Status:** Normative  
**Scope:** authoritative meaning and usage rules for v3 reason IDs.

This document is **normative**. If code or any other documentation conflicts with this file, **this file wins**.

---

## 1. Purpose

Reason IDs exist to make failures and decisions:
- deterministic
- auditable
- machine-readable
- consistent across modules

Reason IDs are used in:
- raised errors (exceptions)
- findings
- reports
- validation messages

---

## 2. Source of Truth

The single source of truth is:

- `adaptive_core.v3.reason_ids.ReasonId`

All reason ID string values MUST be referenced from this enum.  
Do not inline reason ID strings elsewhere.

---

## 3. Fail-Closed Rules

- Unknown reason ID strings MUST NOT be accepted.
- Unknown guardrail IDs MUST be rejected (separate registry enforcement).

When raising `ValueError` for validation failures, the error message MUST include the reason ID prefix.

Example pattern:
- `"{ReasonId.AC_V3_MISSING_FIELD.value}: missing 'timestamp'"`

---

## 4. Category Overview

Below is the intended meaning of key reason IDs (non-exhaustive; enum defines full set).

### 4.1 Input Shape / Schema
- `AC_V3_INVALID_EVENT` — raw input not a mapping or structurally invalid.
- `AC_V3_MISSING_FIELD` — required field missing.
- `AC_V3_TYPE_INVALID` — field present but type invalid or empty where non-empty required.
- `AC_V3_NON_CANONICAL` — value parseable but violates canonical rules.
- `AC_V3_TIMESTAMP_INVALID` — timestamp not ISO8601 or missing trailing `Z`.

### 4.2 Metadata
- `AC_V3_META_INVALID` — meta is not a dict, or contains non-string keys.

### 4.3 Reporting
- `AC_V3_REPORT_INVALID` — canonical JSON missing/invalid, invalid signature status, or report shape invalid.

---

## 5. Logging & Redaction

Reason IDs MUST NOT leak secrets.

- Reason IDs are safe to log.
- Error messages must not include private key material, mnemonics, or PII.
- For user-facing logs, include reason ID but keep details minimal.

---

## 6. Compatibility Note

Reason IDs are part of the v3 contract. Changes that rename, remove, or reinterpret a reason ID are contract-breaking unless versioned explicitly.
