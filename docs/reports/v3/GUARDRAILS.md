# Adaptive Core v3 --- Guardrails Registry

**Version:** v3.0.0\
**Status:** Deterministic guardrails contract (fail-closed)

Guardrails define **hard limits and invariants** that constrain Adaptive
Core behavior.

Guardrails do not execute actions.\
Guardrails define boundaries.

Unknown guardrail IDs MUST fail-closed.

------------------------------------------------------------------------

## 1. Purpose

Guardrails exist to:

-   Define invariant safety limits
-   Constrain upgrade proposals
-   Prevent hidden authority escalation
-   Ensure consistent advisory semantics
-   Enforce explicit contract discipline

Guardrails are referenced by ID in findings and proposals.

------------------------------------------------------------------------

## 2. Guardrail Rules

-   Guardrails are stable identifiers.
-   Guardrails MUST be documented here.
-   Guardrails MUST be validated at runtime.
-   Unknown guardrail IDs MUST trigger explicit reason IDs.
-   Guardrails MUST NOT introduce execution authority.

------------------------------------------------------------------------

## 3. Registry (v3.0.0)

### Core Authority Guardrails

-   `GR_NO_EXECUTION_AUTHORITY`
-   `GR_NO_STATE_MUTATION`
-   `GR_NO_KEY_ACCESS`
-   `GR_NO_AUTO_UPGRADE`
-   `GR_NO_HIDDEN_DEFAULTS`

### Determinism Guardrails

-   `GR_DETERMINISTIC_PIPELINE`
-   `GR_STABLE_CANONICALIZATION`
-   `GR_NO_RANDOMNESS`
-   `GR_NO_TIME_DEPENDENCE`
-   `GR_STABLE_HASH_INPUTS`

### Governance Guardrails

-   `GR_PR_ONLY_UPGRADES`
-   `GR_SCHEMA_STRICT_VALIDATION`
-   `GR_REASON_ID_REGISTRY_LOCK`
-   `GR_GUARDRAIL_REGISTRY_LOCK`
-   `GR_PROPOSAL_EVIDENCE_REQUIRED`

------------------------------------------------------------------------

## 4. Proposals Integration

Upgrade proposals MUST:

-   Reference guardrail IDs explicitly
-   Not violate any listed guardrail
-   Be schema-valid (`proposals/schema/upgrade_proposal_v3.schema.json`)
-   Be submitted via Pull Request only

Violation of guardrails MUST result in fail-closed rejection.

------------------------------------------------------------------------

## 5. Version Discipline

This registry corresponds to v3.0.0.

Adding, removing, or modifying guardrails requires:

-   Contract review (CONTRACT.md)
-   Documentation update
-   Deterministic regression tests
