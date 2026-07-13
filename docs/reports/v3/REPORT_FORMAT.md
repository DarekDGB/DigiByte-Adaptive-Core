# Adaptive Core v3 --- Report Format

**Version:** v3.0.0\
**Status:** Canonical report structure (contract-aligned)

This document defines the deterministic structure of Adaptive Core v3
reports.

If report structure changes in a way that affects field presence,
ordering, hashing inputs, or semantics, that is a contract change and
must be versioned.

------------------------------------------------------------------------

## 1. Pipeline Outputs

Adaptive Core v3 returns four related values:

1.  `UpgradeReportV3` report object
2.  canonical JSON report (machine-readable hashing source)
3.  deterministic Markdown rendering
4.  separate `ReportEnvelopeV3` integrity envelope

The JSON and Markdown are derived from the same report object. The envelope hashes the exact canonical JSON string.

------------------------------------------------------------------------

## 2. Canonical JSON Structure (High-Level)

The canonical JSON is the stable serialization of `UpgradeReportV3` and contains exactly these top-level fields:

```text
report_id
report_type
target_layers
evidence
findings
guardrails
guardrail_titles
confidence
confidence_breakdown
capabilities
drift_dot
recommended_actions
required_tests
exit_criteria
forbidden_actions
```

Serialization uses sorted keys and compact separators. The integrity envelope is separate and is not inserted into this report JSON.

------------------------------------------------------------------------

## 3. Findings Structure

Each finding MUST include:

-   finding_id
-   title
-   severity
-   evidence
-   guardrails

Referenced guardrail IDs are validated against the registry and unknown IDs fail closed. Upstream reason IDs, when present, remain evidence data rather than a separate required finding field.

------------------------------------------------------------------------

## 4. Deterministic Rendering (Markdown)

The Markdown report:

-   Is derived deterministically from the same report object
-   Presents a stable human-readable subset and summary
-   Preserves stable section ordering
-   Avoids non-deterministic formatting artifacts
-   Must not become the hashing source or introduce execution authority

Markdown is a presentation layer only.

------------------------------------------------------------------------

## 5. Integrity Envelope

The in-memory `ReportEnvelopeV3` object includes:

-   `report_hash`
    -   SHA-256 of the exact canonical report JSON string
-   `canonical_json`
    -   the exact string that was hashed and separately returned by the pipeline
-   `classical_signature`
    -   local status metadata: `ABSENT`, `PRESENT`, or `UNSUPPORTED`
-   `pqc_signature`
    -   local status metadata: `ABSENT`, `PRESENT`, or `UNSUPPORTED`

Hash input MUST be canonicalized JSON only.

`ReportEnvelopeV3.to_dict()` emits only `report_hash`, `classical_signature`, and `pqc_signature`. It omits `canonical_json` because the canonical string is already a separate pipeline return value; the string remains observable on the envelope object.

The status values are caller-supplied report metadata. The envelope contains no signature bytes and performs no cryptographic verification. `PRESENT` does not prove a valid Shield signature and grants no approval or execution authority.

------------------------------------------------------------------------

## 6. Shield v4 Boundary

Adaptive Core does not parse Shield signature bundles, select Shield keys, or enforce Shield cryptographic policy. Shield evidence requires `classical-ed25519 + ml-dsa`; optional `fn-dsa` evidence under `fips206-draft-falcon1024-v1` cannot replace or rescue a failed required path and is not final FIPS 206 proof.

Q-ID identity keys and Shield decision-evidence keys remain separate. Adaptive outputs cannot approve, override, downgrade, bypass, or rescue Shield outcomes. AdamantineOS remains the authoritative, fail-closed final policy and execution boundary.

------------------------------------------------------------------------

## 7. Proposals Integration

If a report results in a proposed upgrade:

-   A structured proposal JSON must conform to:
    proposals/schema/upgrade_proposal_v3.schema.json
-   Proposal content must reference:
    -   relevant reason_ids
    -   relevant guardrails
    -   supporting evidence summary
-   Proposal submission occurs via Pull Request only.

Adaptive Core never auto-applies report outcomes.

------------------------------------------------------------------------

## 8. Version Discipline

Any change affecting:

-   required fields
-   hashing inputs
-   ordering guarantees
-   findings structure

requires:

-   contract review
-   deterministic regression tests
-   documentation update
