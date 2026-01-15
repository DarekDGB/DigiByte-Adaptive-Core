# REPORT_FORMAT (v3)

## Purpose

This document defines the **normative** output formats produced by **Adaptive Core v3**:

- Canonical JSON (stable renderer)
- Markdown (stable renderer)
- Integrity envelope (hash + signature status)

**Non-goals:** execution authority, automatic patching, key custody, hidden defaults.

---

## Artifacts produced by the v3 pipeline

`adaptive_core.v3.pipeline.run_v3_pipeline(...)` returns:

1. `UpgradeReportV3` (structured object)
2. `canonical_json: str` (stable JSON rendering of the report)
3. `markdown: str` (stable Markdown rendering of the report)
4. `ReportEnvelopeV3` (hash + signature status)

---

## Canonical JSON (normative)

### Requirements

The canonical JSON string MUST be:

- **Deterministic** for the same report input
- **Stable key ordering**
- **No random fields**
- **No timestamps injected by renderer**
- **UTF-8**

The canonical JSON is what is hashed for integrity in `ReportEnvelopeV3`.

### Top-level structure (high-level)

The report JSON represents an `UpgradeReportV3` object containing (at minimum):

- `report_id`
- `target_layers`
- `capabilities`
- `confidence`
- `evidence_snapshot`
- `findings`
- `guardrails`
- `notes` / `metadata` (if present)

Exact fields are defined by the `UpgradeReportV3` model in code.

---

## Markdown (normative)

The Markdown renderer is a **presentation format** of the same report content.

### Requirements

- Deterministic ordering of sections
- No embedded secrets
- No execution instructions (it is advisory)
- Must include key summary signals:
  - report_id
  - target_layers
  - confidence score (and threshold outcome)
  - evidence counters (snapshot)
  - findings list (with reason_ids)
  - guardrails referenced

---

## Envelope format (normative)

`ReportEnvelopeV3` provides a minimal, integrity-only envelope.

### Fields

- `report_hash`: SHA-256 hex digest of the canonical JSON string
- `canonical_json`: the full canonical JSON string (included to make the envelope self-contained)
- `classical_signature`: one of `ABSENT | PRESENT | UNSUPPORTED`
- `pqc_signature`: one of `ABSENT | PRESENT | UNSUPPORTED`

### Guardrails

- **No silent fallback** for signature status
- Invalid status value MUST raise `AC_V3_REPORT_INVALID`
- Hash MUST be computed over `canonical_json` exactly as produced

---

## Compatibility notes

- Any **semantic change** to the report structure must follow contract discipline (major bump if breaking).
- Renderers may evolve visually, but must remain deterministic.
