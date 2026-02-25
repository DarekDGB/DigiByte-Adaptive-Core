# Adaptive Core --- Upgrade Proposals Mailbox

This directory is the **structured upgrade proposals mailbox** for
Adaptive Core.

Proposals are **advisory governance artifacts**. They are
**human-reviewed** and submitted via Pull Request.

Adaptive Core is **mailbox + validator + reporter**. It never applies
upgrades automatically.

------------------------------------------------------------------------

## 1. Directory Structure

-   `schema/` --- authoritative JSON schemas for proposals
-   `template/` --- proposal templates
-   `inbox/` --- proposals submitted via Pull Request (optional folder
    if used)
-   `examples/` --- example proposals (optional)

------------------------------------------------------------------------

## 2. Submission Rules (PR-Only)

All proposals MUST:

-   Conform to the v3 schema: `schema/upgrade_proposal_v3.schema.json`
-   Be submitted via Pull Request
-   Include supporting evidence references (reason IDs + findings
    summary)
-   Declare intended scope and risk explicitly
-   Remain deterministic (no time-based or random fields)

Any proposal failing schema or governance rules MUST be rejected.

------------------------------------------------------------------------

## 3. Validation Model

Validation is strict and fail-closed:

-   Unknown fields are rejected
-   Unknown reason IDs are rejected
-   Unknown guardrail IDs are rejected
-   Missing required evidence is rejected

This prevents hidden authority escalation.

------------------------------------------------------------------------

## 4. Review Expectations

A reviewer SHOULD confirm:

-   The proposal is schema-valid
-   Evidence justification is sufficient
-   No guardrails are violated
-   The proposal does not imply auto-upgrades or execution authority
-   The proposed change has deterministic tests attached (where
    applicable)

------------------------------------------------------------------------

## 5. Relationship to External Systems

External systems (e.g., execution boundaries such as AdamantineOS) may:

-   Generate structured proposals
-   Submit them here for review

Adaptive Core never pushes upgrades outward.

------------------------------------------------------------------------

## 6. Version Discipline

Proposal schema changes require:

-   Contract review (docs/reports/v3/CONTRACT.md)
-   Deterministic regression tests
-   Documentation updates
