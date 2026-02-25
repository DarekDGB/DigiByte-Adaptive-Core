# Adaptive Core v3 --- Documentation Index

**Version:** v3.0.0\
**Status:** Contract-aligned documentation index

This index reflects the shipped v3.0.0 implementation and its normative
contract surface.

If documentation and code diverge, **code + CONTRACT.md wins**.

------------------------------------------------------------------------

## Core Normative Documents

-   `README.md` --- v3 overview and high-level guarantees
-   `CONTRACT.md` --- normative behavior contract (authoritative)
-   `AUTHORITY_BOUNDARIES.md` --- hard authority limits
-   `GUARDRAILS.md` --- enforced guardrails registry
-   `SECURITY.md` --- security posture & disclosure process

------------------------------------------------------------------------

## Models & Deterministic Logic

-   `EVIDENCE_STORE.md` --- bounded evidence window semantics
-   `CORRELATION.md` --- deterministic correlation logic
-   `DRIFT_RADAR.md` --- drift detection model
-   `CONFIDENCE_MODEL.md` --- confidence scoring rules
-   `REASON_IDS.md` --- stable reason identifier registry

------------------------------------------------------------------------

## Reporting & Execution Flow

-   `REPORT_FORMAT.md` --- canonical JSON + Markdown report structure
-   `PIPELINE_USAGE.md` --- deterministic invocation + pipeline
    guarantees
-   `NODE_SUMMARY.md` --- privacy-preserving cross-node aggregation

------------------------------------------------------------------------

## Upgrade Governance

Adaptive Core v3 includes a structured upgrade proposal mailbox:

-   Repository root: `proposals/`
-   Schema: `proposals/schema/upgrade_proposal_v3.schema.json`
-   Templates: `proposals/template/`
-   Submission method: Pull Request only (human-reviewed)

Adaptive Core acts as **mailbox + validator + reporter**.

It never auto-applies upgrades.

------------------------------------------------------------------------

## Version Discipline

This documentation set corresponds to:

**Adaptive Core v3.0.0**

Any structural or behavioral change that affects:

-   validation
-   canonicalization
-   report structure
-   integrity hashing
-   proposal schema

requires:

-   explicit documentation update
-   deterministic regression tests
-   contract version review
