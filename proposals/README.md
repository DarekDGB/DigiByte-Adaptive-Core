# Adaptive Core — Upgrade Proposals Mailbox + Outbox

This directory is the **structured upgrade proposals governance area** for Adaptive Core.

Proposals are **advisory governance artifacts**:
- **Adaptive Core may propose**
- **Humans review**
- **Humans apply changes via Pull Request**
- Adaptive Core **never** auto-applies upgrades

------------------------------------------------------------------------

## 1. Directory Structure

- `schema/` — authoritative JSON schemas for proposals
- `template/` — proposal templates
- `inbox/` — proposals submitted via Pull Request (optional workflow)
- `outbox/` — **generated sealed artifacts** emitted by ACv3 tooling

Notes:

- `inbox/` is for PR submission inside this repo (optional).
- `outbox/` is for **artifact generation**. Humans still decide what becomes a PR.

------------------------------------------------------------------------

## 2. Submission Rules (PR-Only)

All proposals MUST:

- Conform to the v3 schema: `schema/upgrade_proposal_v3.schema.json`
- Be human-reviewed and submitted via Pull Request (in this repo or elsewhere)
- Declare intended scope and risk explicitly
- Remain deterministic (no time-based or random fields beyond explicit timestamps)
- Never imply auto-upgrades or execution authority

Any proposal failing schema or governance rules MUST be rejected.

------------------------------------------------------------------------

## 3. Validation Model (Fail-Closed)

Validation is strict and fail-closed:

- Unknown fields are rejected
- Unknown reason IDs are rejected
- Unknown guardrail IDs are rejected
- Hash mismatch is rejected

This prevents hidden authority escalation.

------------------------------------------------------------------------

## 4. Outbox Model (Generated Artifacts)

ACv3 tooling can emit sealed proposals into `outbox/`:

- File name is deterministic and derived from `proposal_id` + `proposal_hash`
- If the same file already exists with the same bytes, emission is idempotent
- If the file exists with different bytes, emission fails closed

Outbox emission is **not execution**. It is **artifact production**.

------------------------------------------------------------------------

## 5. Review Expectations

A reviewer SHOULD confirm:

- The proposal is schema-valid
- Evidence justification is sufficient
- No guardrails are violated
- The proposal does not imply auto-upgrades or execution authority
- The proposed change has deterministic tests attached (where applicable)

------------------------------------------------------------------------

## 6. Relationship to External Systems

Execution boundaries (e.g., Adamantine Wallet OS) may:

- Consume proposal artifacts
- Require human review receipts
- Enforce strict validation before any decision is allowed

Adaptive Core never pushes upgrades outward and never applies them.
