# Adaptive Core v3 --- Reason IDs

**Version:** v3.0.0\
**Status:** Stable identifier registry (contract-aligned)

Reason IDs are stable machine identifiers used to explain why a finding,
denial, or advisory output occurred.

Reason IDs exist to enforce:

-   determinism
-   explainability
-   auditability
-   upgrade governance discipline

Unknown reason IDs MUST fail-closed.

------------------------------------------------------------------------

## 1. Rules

-   Reason IDs are strings with stable formatting.
-   Reason IDs are never guessed or inferred.
-   Any new reason ID requires:
    -   doc update here
    -   deterministic regression test coverage
    -   contract review for semantic impact

------------------------------------------------------------------------

## 2. Structure

Recommended pattern:

ACV3\_`<DOMAIN>`{=html}\_`<DETAIL>`{=html}

Examples:

-   ACV3_SCHEMA_INVALID
-   ACV3_CANONICALIZE_FAILED
-   ACV3_GUARDRAIL_UNKNOWN
-   ACV3_INTEGRITY_MISMATCH
-   ACV3_EVIDENCE_WINDOW_OVERFLOW

------------------------------------------------------------------------

## 3. Registry (v3.0.0)

### Input / Validation

-   ACV3_SCHEMA_INVALID --- input fails strict schema validation
-   ACV3_CANONICALIZE_FAILED --- canonicalization could not be performed
-   ACV3_UNKNOWN_FIELD --- input contains unknown/forbidden fields
-   ACV3_GUARDRAIL_UNKNOWN --- referenced guardrail ID not found in
    registry
-   ACV3_REASON_ID_UNKNOWN --- referenced reason ID not known/stable

### Evidence / Analysis

-   ACV3_EVIDENCE_WINDOW_OVERFLOW --- evidence window bounds exceeded
-   ACV3_EVIDENCE_INVALID --- evidence payload failed validation
    constraints
-   ACV3_CORRELATION_INVALID --- correlation computation failed
    determinism rules
-   ACV3_DRIFT_SIGNAL --- drift indicator triggered (when drift
    contracts exist)

### Reporting / Integrity

-   ACV3_REPORT_BUILD_FAILED --- report builder failed deterministically
-   ACV3_CONTEXT_HASH_FAILED --- context hash could not be computed
-   ACV3_INTEGRITY_MISMATCH --- integrity envelope mismatch detected

### Proposals

-   ACV3_PROPOSAL_SCHEMA_INVALID --- proposal fails schema validation
-   ACV3_PROPOSAL_FORBIDDEN_CHANGE --- proposal violates guardrails /
    authority bounds
-   ACV3_PROPOSAL_MISSING_EVIDENCE --- proposal lacks required
    supporting evidence refs

------------------------------------------------------------------------

## 4. Proposals Linkage

Upgrade proposals MUST reference reason IDs from this registry.\
Proposal schema: proposals/schema/upgrade_proposal_v3.schema.json

Unknown reason IDs in proposals MUST fail-closed.

------------------------------------------------------------------------

## 5. Version Discipline

This registry corresponds to v3.0.0.

Any additions or semantic changes require:

-   contract review (CONTRACT.md)
-   deterministic tests
-   documentation update here
