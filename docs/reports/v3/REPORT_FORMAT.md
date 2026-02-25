# Adaptive Core v3 --- Report Format

**Version:** v3.0.0\
**Status:** Canonical report structure (contract-aligned)

This document defines the deterministic structure of Adaptive Core v3
reports.

If report structure changes in a way that affects field presence,
ordering, hashing inputs, or semantics, that is a contract change and
must be versioned.

------------------------------------------------------------------------

## 1. Report Artifacts

Adaptive Core v3 produces two synchronized artifacts:

1.  Canonical JSON report (machine-readable, hashing source)
2.  Markdown report (human-readable rendering of same content)

Both must represent identical semantic content.

------------------------------------------------------------------------

## 2. Canonical JSON Structure (High-Level)

The canonical report JSON includes:

-   version --- report contract version (v3)
-   observations_summary --- deterministic summary of processed inputs
-   evidence_window --- bounded counters and metrics
-   findings --- array of structured findings
-   confidence --- deterministic confidence model output
-   guardrails --- referenced guardrail IDs
-   reason_ids --- referenced reason identifiers
-   metadata
    -   pipeline_version
-   integrity
    -   context_hash (computed over canonical JSON)
    -   signature_status (present/absent/invalid)

Field ordering must be stable after canonicalization.

------------------------------------------------------------------------

## 3. Findings Structure

Each finding MUST include:

-   reason_id (stable registry reference)
-   severity
-   description
-   evidence_refs
-   guardrail_refs

Unknown reason IDs or guardrail IDs MUST fail-closed.

------------------------------------------------------------------------

## 4. Deterministic Rendering (Markdown)

The Markdown report:

-   Mirrors the canonical JSON content
-   Preserves stable section ordering
-   Avoids non-deterministic formatting artifacts
-   Must not introduce new semantic data not present in JSON

Markdown is a presentation layer only.

------------------------------------------------------------------------

## 5. Integrity Envelope

The integrity envelope includes:

-   context_hash
    -   Deterministically computed from canonical JSON
-   signature_status
    -   Explicit status only (no implied authority)

Hash input MUST be canonicalized JSON only.

------------------------------------------------------------------------

## 6. Proposals Integration

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

## 7. Version Discipline

Any change affecting:

-   required fields
-   hashing inputs
-   ordering guarantees
-   findings structure

requires:

-   contract review
-   deterministic regression tests
-   documentation update
