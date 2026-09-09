# Adaptive Core v3 --- Security Policy

**Package baseline:** v3.1.0\
**Status:** Deterministic, fail-closed advisory system

Adaptive Core v3 is a read-only, deterministic advisory engine. It does
not execute transactions, hold keys, or modify external systems.

Security posture is defined by:

-   Deterministic execution
-   Fail-closed validation
-   Strict authority boundaries
-   100% statement coverage (CI-enforced)
-   Human-reviewed governance (PR-only proposals)

------------------------------------------------------------------------

## 1. Reporting Security Issues

If you discover a security vulnerability or boundary violation, please
report it responsibly:

Email: **adamantinewalletos@gmail.com**

Please include:

-   Description of the issue
-   Steps to reproduce
-   Affected package version and exact commit
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
-   Verify Shield signatures or select Shield trust keys

Read-only is an external authority limit, not a claim of zero local state.
The implementation supports local evidence counters and explicit artifact
output. Those outputs cannot approve, override, downgrade, bypass, or rescue
Shield or AdamantineOS policy. AdamantineOS remains the authoritative,
fail-closed final policy and execution boundary.

Report hashes provide deterministic integrity checks. Caller-supplied
`classical_signature` and `pqc_signature` labels (`ABSENT`, `PRESENT`,
`UNSUPPORTED`) are not signature bytes or verified Shield proof. Adaptive Core
has no OQS workflow and makes no live-OQS or final FIPS 206 claim.

------------------------------------------------------------------------

## 3. Deterministic Security Guarantees

Security relies on:

-   No randomness
-   No implicit wall-clock input in deterministic v3 report decisions
-   Explicit time inputs for advisory freshness validation when supplied
-   Stable canonical JSON hashing
-   Regression-locked contract behavior

Any nondeterministic behavior is treated as a defect.

This is a tested contract, not a production certification or a claim that
every environmental condition and optional persistence path has been proven.

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

This policy covers the v3 advisory implementation under package baseline
v3.1.0. G2 aligns package metadata to the existing tag and public baseline;
it does not declare a new release. The v3.0.0 report-document baseline and
the exporter's `adaptive-core/3.0.0` default remain frozen compatibility data.
The default is caller-overridable metadata, not verified source identity.
See [release status](docs/RELEASE_STATUS_V4_10_G2.md) for the exact version map.

Changes to:

-   Validation logic
-   Canonicalization rules
-   Report structure
-   Proposal schema

require documentation update and regression test coverage.
