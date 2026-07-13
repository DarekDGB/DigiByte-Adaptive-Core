# Adaptive Core --- Reports Documentation Index

**Version:** v3.0.0\
**Status:** Documentation set aligned with contract + implementation

This index covers the Adaptive Core reporting and governance
documentation.

If documentation diverges from implementation, **code + CONTRACT.md
wins**.

------------------------------------------------------------------------

# v3 Documentation Set

All v3 normative documentation lives under:

docs/reports/v3/

Core documents:

-   README.md --- v3 overview
-   CONTRACT.md --- normative behavior contract (authoritative)
-   AUTHORITY_BOUNDARIES.md --- hard authority limits
-   ADAMANTINEOS_INTEGRATION.md --- advisory exporter and Shield v4 compatibility boundary
-   ARCHITECTURE_OVERVIEW.md --- current Adaptive Core topology
-   ADAPTIVE_CORE_V3_DIAGRAMS.md --- architecture diagrams
-   GUARDRAILS.md --- enforced guardrails registry
-   [`../../SECURITY.md`](../../SECURITY.md) --- repository security posture and disclosure policy

Deterministic Logic:

-   EVIDENCE_STORE.md --- bounded evidence window model
-   CORRELATION.md --- deterministic correlation model
-   DRIFT_RADAR.md --- contract-defined drift detection
-   CONFIDENCE_MODEL.md --- deterministic confidence scoring
-   REASON_IDS.md --- stable reason ID registry

Reporting & Flow:

-   REPORT_FORMAT.md --- canonical JSON + Markdown structure
-   PIPELINE_USAGE.md --- deterministic invocation guarantees
-   NODE_SUMMARY.md --- privacy-preserving cross-node aggregation

------------------------------------------------------------------------

# Governance & Upgrade Flow

Structured upgrade proposals live at repository root:

proposals/

Governance model:

-   Schema-validated proposals only
-   Pull Request submission required
-   Human-reviewed approval required
-   No auto-upgrades
-   Fail-closed validation model

Adaptive Core acts as:

-   Mailbox
-   Validator
-   Reporter

It never executes changes.

------------------------------------------------------------------------

# Legacy v2 Documentation

Historical v2 reports are indexed by [`v2/README.md`](v2/README.md). They are non-normative for Adaptive Core v3 and Shield v4.

------------------------------------------------------------------------

# Version Discipline

This documentation set corresponds to:

Adaptive Core v3 contract documentation

Any change affecting:

-   validation logic
-   canonicalization rules
-   hashing inputs
-   report structure
-   proposal schema

requires:

-   documentation update
-   regression test coverage
-   contract review
