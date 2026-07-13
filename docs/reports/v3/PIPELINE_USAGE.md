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
6.  Compute the integrity envelope (`report_hash` over canonical report JSON).
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

Validation failures MUST reject the call through the applicable
fail-closed exception path. The pipeline does not define or return a
structured failure object, and it MUST NOT emit partial advisory output
after rejection.

It must never silently downgrade behavior or convert rejection into an
advisory success.

------------------------------------------------------------------------

## 4. Advisory Output Structure

The pipeline returns:

-   report object (including `findings[]`)
-   report_json (canonical)
-   report_markdown (rendered view)
-   `ReportEnvelopeV3` integrity-envelope object:
    -   report_hash
    -   canonical_json (the exact string also returned as `report_json`)
    -   classical_signature (`ABSENT`, `PRESENT`, or `UNSUPPORTED`)
    -   pqc_signature (`ABSENT`, `PRESENT`, or `UNSUPPORTED`)

These outputs are advisory and require human review.
The signature fields are local caller-supplied status metadata. They do not contain signature bytes and do not prove cryptographic verification.
The envelope object's `to_dict()` view omits `canonical_json` and emits the other three fields.

------------------------------------------------------------------------

## 5. Integration Model

External systems such as AdamantineOS:

-   Call Adaptive Core with strict v3 observations.
-   Receive advisory output.
-   Optionally generate structured upgrade proposals.
-   Submit proposals to the repository `proposals/` mailbox via Pull
    Request.

Adaptive Core never pushes updates outward.
AdamantineOS independently verifies Shield evidence under verifier-controlled policy and remains the authoritative, fail-closed final policy and execution boundary.

------------------------------------------------------------------------

## 6. What the Pipeline Is NOT

The pipeline is not:

-   A transaction processor
-   A consensus engine
-   An auto-remediation engine
-   A governance automation system
-   A Shield signature verifier or Shield key selector

It is a deterministic intelligence layer only.

------------------------------------------------------------------------

## 7. Shield v4 Compatibility

Shield evidence requires `classical-ed25519 + ml-dsa`. Optional `fn-dsa` evidence uses Falcon-1024 under `fips206-draft-falcon1024-v1`; it cannot replace or rescue failed required evidence and is not final FIPS 206 proof.

Adaptive Core does not enforce that cryptographic policy. Q-ID identity keys and Shield decision-evidence keys remain separate. Adaptive output cannot approve, override, downgrade, bypass, or rescue a Shield result.
