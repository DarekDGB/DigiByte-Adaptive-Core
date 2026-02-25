# Adaptive Core v3 --- Pipeline Usage

**Version:** v3.0.0\
**Status:** Deterministic, read-only invocation contract

This document describes how Adaptive Core v3 is invoked and what
guarantees the execution pipeline provides.

Adaptive Core is a deterministic advisory engine. It is not an executor.

------------------------------------------------------------------------

## 1. High-Level Invocation Model

Adaptive Core v3 follows a strict flow:

1.  Receive v3-shaped observations (schema-valid).
2.  Canonicalize input (stable ordering, normalization).
3.  Process through deterministic evidence window.
4.  Derive findings (including optional drift signals).
5.  Build canonical report artifacts (JSON + Markdown).
6.  Compute integrity envelope (context_hash).
7.  Return advisory output to caller.

No step mutates external systems.

------------------------------------------------------------------------

## 2. Determinism Guarantees

The pipeline MUST:

-   Reject malformed or ambiguous input (fail-closed).
-   Avoid random or time-based logic.
-   Avoid environment-dependent branching.
-   Maintain stable ordering in JSON artifacts.
-   Produce identical outputs for identical canonical inputs.

Determinism is enforced by tests and coverage gate (100%).

------------------------------------------------------------------------

## 3. Failure Model (Fail-Closed)

If any of the following occur:

-   Schema violation
-   Unknown guardrail ID
-   Unknown reason ID
-   Invalid canonicalization state
-   Integrity mismatch

The pipeline MUST return a structured failure with explicit reason
identifiers.

It must never silently downgrade behavior.

------------------------------------------------------------------------

## 4. Advisory Output Structure

The pipeline returns:

-   findings\[\]
-   report_json (canonical)
-   report_markdown (rendered view)
-   integrity_envelope:
    -   context_hash
    -   signature_status

These outputs are advisory and require human review.

------------------------------------------------------------------------

## 5. Integration Model

External systems (e.g., execution boundaries such as AdamantineOS):

-   Call Adaptive Core with strict v3 observations.
-   Receive advisory output.
-   Optionally generate structured upgrade proposals.
-   Submit proposals to the repository `proposals/` mailbox via Pull
    Request.

Adaptive Core never pushes updates outward.

------------------------------------------------------------------------

## 6. What the Pipeline Is NOT

The pipeline is not:

-   A transaction processor
-   A consensus engine
-   An auto-remediation engine
-   A governance automation system

It is a deterministic intelligence layer only.
