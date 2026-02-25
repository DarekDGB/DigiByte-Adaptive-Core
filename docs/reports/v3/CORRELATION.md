# Adaptive Core v3 --- Correlation Model

**Version:** v3.0.0\
**Status:** Deterministic correlation layer (contract-aligned)

The Correlation layer derives structured relationships between
validated, canonicalized observations within the bounded Evidence Store.

It is deterministic, explainable, and advisory-only.

------------------------------------------------------------------------

## 1. Purpose

Correlation exists to:

-   Detect structured relationships between signals
-   Identify co-occurrence patterns
-   Support drift and anomaly indicators
-   Provide explainable context for findings

It does not introduce probabilistic or black-box inference.

------------------------------------------------------------------------

## 2. Determinism Requirements

Correlation MUST:

-   Operate only on canonicalized inputs
-   Use stable ordering (no set-order nondeterminism)
-   Avoid randomness
-   Avoid time-based branching
-   Produce identical outputs for identical Evidence Store states

All correlation outputs must be replayable.

------------------------------------------------------------------------

## 3. Allowed Operations

Deterministic correlation may include:

-   Counter co-occurrence checks
-   Threshold comparisons
-   Deterministic graph traversal
-   Stable aggregation of related reason IDs
-   Explicit drift signal propagation (if contract-defined)

All operations must be explainable and reproducible.

------------------------------------------------------------------------

## 4. Forbidden Behavior

Correlation MUST NOT:

-   Introduce heuristic guessing
-   Use machine learning models
-   Modify Evidence Store state
-   Mutate external systems
-   Generate findings without traceable evidence references

All correlation outputs must reference explicit evidence entries.

------------------------------------------------------------------------

## 5. Output Structure

Correlation outputs feed into the Findings layer and may include:

-   Related observation groups
-   Correlated reason IDs
-   Drift signal markers
-   Confidence contribution inputs

Correlation never produces final advisory output directly.

------------------------------------------------------------------------

## 6. Failure Model

Correlation MUST fail-closed when:

-   Evidence references are missing
-   Canonicalization assumptions are violated
-   Guardrail references are invalid
-   Threshold definitions are malformed

Failures must return explicit reason IDs.

------------------------------------------------------------------------

## 7. Scope Boundaries

Correlation is not:

-   A predictive engine
-   A governance authority
-   A risk scoring black box
-   A consensus modifier

It is a deterministic relational analysis component only.
