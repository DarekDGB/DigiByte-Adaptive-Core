# Adaptive Core v3 --- Node Summary

**Version:** v3.0.0\
**Status:** Privacy-preserving deterministic aggregation
(contract-aligned)

Node Summary defines how Adaptive Core v3 may aggregate advisory signals
across multiple nodes without violating authority boundaries or privacy
guarantees.

Node Summary is advisory-only.

------------------------------------------------------------------------

## 1. Purpose

Node Summary exists to:

-   Aggregate deterministic findings across nodes
-   Detect cross-node pattern consistency
-   Provide ecosystem-level advisory visibility
-   Support human-reviewed upgrade decisions

It does not alter node state or network consensus.

------------------------------------------------------------------------

## 2. Determinism Requirements

Node Summary MUST:

-   Operate only on canonicalized report artifacts
-   Use stable ordering for aggregation
-   Avoid randomness
-   Avoid time-based branching
-   Produce identical outputs for identical input report sets

Cross-node summaries must be replayable.

------------------------------------------------------------------------

## 3. Privacy Guarantees

Node Summary MUST:

-   Avoid storing raw sensitive data
-   Avoid exposing private node metadata
-   Aggregate using minimal necessary signal references
-   Preserve anonymity where applicable

Only deterministic, contract-defined fields may be aggregated.

------------------------------------------------------------------------

## 4. Allowed Aggregation

Deterministic aggregation may include:

-   Count of identical reason IDs across nodes
-   Drift signal frequency distribution
-   Confidence score distribution buckets
-   Guardrail reference frequency
-   Stable correlation overlap metrics

No probabilistic or heuristic clustering is allowed.

------------------------------------------------------------------------

## 5. Output Shape

A node summary SHOULD include:

-   aggregated_reason_counts
-   drift_frequency_summary
-   confidence_distribution
-   guardrail_reference_counts
-   integrity_hash_of_input_set

The integrity hash must be computed over canonicalized input reports
only.

------------------------------------------------------------------------

## 6. Failure Model

Node Summary MUST fail-closed when:

-   Input report schema is invalid
-   Integrity hashes mismatch
-   Canonicalization assumptions are violated
-   Unknown reason IDs or guardrails appear

Failures must return explicit reason IDs.

------------------------------------------------------------------------

## 7. Authority Boundary

Node Summary is not:

-   A coordination layer
-   A voting mechanism
-   A governance trigger
-   A consensus modifier

It is a deterministic advisory aggregation component only.
