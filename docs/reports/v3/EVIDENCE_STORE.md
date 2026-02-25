# Adaptive Core v3 --- Evidence Store

**Version:** v3.0.0\
**Status:** Deterministic bounded evidence window (contract-aligned)

The Evidence Store is a deterministic, bounded, replayable structure
used by Adaptive Core v3 to accumulate signal counts and contextual
metrics.

It exists to support advisory findings --- not autonomous action.

------------------------------------------------------------------------

## 1. Purpose

The Evidence Store:

-   Aggregates validated v3 observations
-   Maintains bounded counters (hot-window semantics)
-   Supports deterministic replay
-   Prevents unbounded growth or hidden state

It MUST remain memory-safe and bounded.

------------------------------------------------------------------------

## 2. Determinism Rules

The Evidence Store MUST:

-   Produce identical internal state for identical ordered inputs
-   Avoid random sampling
-   Avoid time-based logic
-   Avoid environment-dependent branching
-   Maintain stable iteration ordering

Inputs must be canonicalized before insertion.

------------------------------------------------------------------------

## 3. Bounded Window Semantics

The store uses a bounded hot-window model:

-   Only recent observations (within defined window constraints) are
    retained
-   Window bounds are deterministic
-   Overflow conditions MUST trigger explicit reason identifiers
-   Old entries are pruned deterministically

No implicit eviction policies are allowed.

------------------------------------------------------------------------

## 4. Failure Model

The Evidence Store MUST fail-closed when:

-   Input schema is invalid
-   Canonicalization fails
-   Window bounds are exceeded unexpectedly
-   Correlation inputs are malformed

Failures must return explicit reason IDs.

------------------------------------------------------------------------

## 5. Interaction with Findings

Findings derive from:

-   Aggregated counters
-   Correlation outputs
-   Drift indicators (if explicit contracts exist)

The Evidence Store never produces findings directly --- it only supplies
structured inputs to the analysis layer.

------------------------------------------------------------------------

## 6. Integration with Reports

Report artifacts may include:

-   Evidence summaries
-   Counter snapshots
-   Window metrics

All summaries must be deterministic projections of the Evidence Store
state.

------------------------------------------------------------------------

## 7. Out of Scope

The Evidence Store is not:

-   A persistent database
-   A distributed consensus store
-   A logging system
-   A governance engine

It is a deterministic in-memory advisory component only.
