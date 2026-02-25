# Adaptive Core v3 --- Confidence Model

**Version:** v3.0.0\
**Status:** Deterministic confidence scoring (contract-aligned)

The Confidence Model produces a deterministic confidence score that
accompanies findings and advisory reports.

It quantifies signal strength --- it does not authorize action.

------------------------------------------------------------------------

## 1. Purpose

The Confidence Model exists to:

-   Quantify strength of accumulated evidence
-   Reflect correlation density and stability
-   Provide consistent scoring for human review
-   Support upgrade proposal justification

Confidence is advisory context only.

------------------------------------------------------------------------

## 2. Determinism Requirements

The Confidence Model MUST:

-   Operate only on canonicalized inputs
-   Use bounded evidence window data
-   Avoid randomness
-   Avoid time-based branching
-   Produce identical scores for identical input state

Confidence scoring must be replayable.

------------------------------------------------------------------------

## 3. Inputs

Confidence may incorporate:

-   Evidence counters
-   Correlation density
-   Drift persistence duration
-   Guardrail impact weighting (contract-defined only)
-   Finding consistency across window

All inputs must be deterministic projections of the Evidence Store and
correlation outputs.

------------------------------------------------------------------------

## 4. Output Format

Confidence output SHOULD include:

-   `score` (numeric, bounded range, e.g., 0.0 -- 1.0)
-   `level` (e.g., LOW / MEDIUM / HIGH --- deterministic mapping)
-   `explanation_refs` (evidence + reason_ids contributing to score)

Confidence must never introduce hidden weighting logic.

------------------------------------------------------------------------

## 5. Forbidden Behavior

The Confidence Model MUST NOT:

-   Use machine learning
-   Use probabilistic estimation
-   Modify findings
-   Override guardrails
-   Imply authority or enforcement

Confidence reflects signal clarity, not governance power.

------------------------------------------------------------------------

## 6. Failure Model

Confidence scoring MUST fail-closed when:

-   Required inputs are missing
-   Evidence window state is inconsistent
-   Correlation outputs are invalid
-   Guardrail references are unknown

Failures must return explicit reason IDs.

------------------------------------------------------------------------

## 7. Authority Boundary

Confidence is:

-   Not an approval engine
-   Not an execution trigger
-   Not an automatic upgrade threshold

It is a deterministic advisory metric only.
