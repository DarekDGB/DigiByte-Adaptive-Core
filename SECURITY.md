# Adaptive Core v3 --- Security Policy

**Version:** v3.0.0\
**Status:** Deterministic, fail-closed advisory system

Adaptive Core v3 is a read-only, deterministic advisory engine. It does
not execute transactions, hold keys, or modify external systems.

Security posture is defined by:

-   Deterministic execution
-   Fail-closed validation
-   Strict authority boundaries
-   100% test coverage (CI-enforced)
-   Human-reviewed governance (PR-only proposals)

------------------------------------------------------------------------

## 1. Reporting Security Issues

If you discover a security vulnerability or boundary violation, please
report it responsibly:

Email: **adamantinewalletos@gmail.com**

Please include:

-   Description of the issue
-   Steps to reproduce
-   Affected version (e.g., v3.0.0)
-   Proof-of-concept (if applicable)
-   Expected vs actual behavior

Do NOT open a public issue for critical vulnerabilities.

------------------------------------------------------------------------

## 2. Scope of Security Model

Adaptive Core v3 enforces:

-   Strict schema validation (fail-closed)
-   Deterministic canonicalization
-   Stable integrity hashing
-   Guardrail registry validation
-   Reason ID registry locking
-   Proposal schema validation (PR-only governance)

It does NOT:

-   Hold private keys
-   Sign transactions
-   Modify wallet or node state
-   Auto-apply upgrades
-   Provide hidden authority

------------------------------------------------------------------------

## 3. Deterministic Security Guarantees

Security relies on:

-   No randomness
-   No time-based logic
-   No environment-dependent branching
-   Stable canonical JSON hashing
-   Regression-locked contract behavior

Any nondeterministic behavior is treated as a defect.

------------------------------------------------------------------------

## 4. Upgrade Governance Security

Upgrade proposals must:

-   Conform to `proposals/schema/upgrade_proposal_v3.schema.json`
-   Be submitted via Pull Request
-   Pass strict validation (unknown fields rejected)
-   Reference valid guardrail and reason IDs
-   Undergo explicit human review

Adaptive Core never auto-merges or auto-applies upgrades.

------------------------------------------------------------------------

## 5. Severity Guidelines

Critical (Severity 1):

-   Boundary violation (execution authority introduced)
-   Hidden authority path
-   Nondeterministic behavior affecting outputs
-   Schema bypass

High:

-   Integrity hash mismatch
-   Guardrail registry inconsistency
-   Proposal validation bypass

Medium:

-   Documentation-contract mismatch
-   Missing fail-closed validation path

------------------------------------------------------------------------

## 6. Disclosure Policy

Responsible disclosure is expected.

We aim to:

-   Acknowledge receipt within reasonable time
-   Provide remediation timeline where possible
-   Release patch with regression tests
-   Update documentation and contract if required

------------------------------------------------------------------------

## 7. Version Discipline

This security policy corresponds to v3.0.0.

Changes to:

-   Validation logic
-   Canonicalization rules
-   Report structure
-   Proposal schema

require documentation update and regression test coverage.
