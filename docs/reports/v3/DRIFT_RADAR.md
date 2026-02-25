# Adaptive Core v3 --- Drift Radar

**Version:** v3.0.0\
**Status:** Deterministic drift indicator model (contract-aligned)

Drift Radar is a deterministic model for detecting contract-defined
drift in shield signals and system behavior over a bounded evidence
window.

It produces advisory drift indicators only.

------------------------------------------------------------------------

## 1. Purpose

Drift Radar exists to:

-   Detect deviations from expected behavior
-   Highlight sustained signal shifts
-   Support human-reviewed upgrade decisions
-   Provide explainable drift findings

Drift Radar does not autonomously remediate or upgrade anything.

------------------------------------------------------------------------

## 2. Determinism Requirements

Drift Radar MUST:

-   operate on canonicalized inputs only
-   use bounded evidence window state
-   avoid time-based branching (no wall-clock time dependencies)
-   avoid randomness
-   produce identical outputs for identical inputs

------------------------------------------------------------------------

## 3. Drift Requires a Contract

Drift indicators MUST NOT be guessed.

Drift detection MUST be anchored to one or more explicit contracts, such
as:

-   expected ranges / thresholds
-   allowed variance bands
-   expected correlation relationships
-   explicit invariants defined in CONTRACT.md or policy documents

If no contract exists, the Drift Radar may only report raw trend
summaries, not drift findings.

------------------------------------------------------------------------

## 4. Drift Signal Types (Advisory)

Allowed deterministic drift indicators include:

-   sustained threshold breaches (over N observations)
-   monotonic trend persistence (over bounded window)
-   correlation structure changes (contract-defined)
-   unexpected distribution skew (deterministic buckets)

All drift indicators must reference evidence and reason IDs.

------------------------------------------------------------------------

## 5. Output Shape

A drift indicator SHOULD include:

-   reason_id (stable)
-   severity
-   description
-   evidence_refs
-   window_summary
-   contract_ref (the rule/invariant that was violated)

------------------------------------------------------------------------

## 6. Failure Model

Drift Radar MUST fail-closed when:

-   contract references are missing/invalid (for drift findings)
-   evidence window state is inconsistent
-   canonicalization assumptions are violated

------------------------------------------------------------------------

## 7. Authority Boundaries

Drift Radar is not:

-   an autonomous anomaly response system
-   a governance authority
-   a predictive ML model

It is a deterministic advisory layer only.
