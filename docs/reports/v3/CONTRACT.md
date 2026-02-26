# Adaptive Core v3 --- CONTRACT (Normative)

**Status:** Normative • Contract-Locking Document\
**Scope:** `adaptive_core.v3.*` (read-only upgrade oracle)

This document is **normative**. If other docs diverge, **this file
wins**.\
If **code** diverges from this contract, that is a **bug** and must be
fixed with a regression test.

------------------------------------------------------------------------

## 1. Purpose

Adaptive Core v3 ("ACv3") is the **Upgrade Oracle** for the DigiByte
Quantum Shield.

It ingests **strict, canonicalized, v3-shaped observations** and
produces **deterministic advisory outputs**:

-   evidence counters (bounded hot window)
-   findings (including optional drift findings when explicit contracts
    are provided)
-   upgrade reports (canonical JSON + stable Markdown)
-   integrity envelope (deterministic hash + explicit signature status)

ACv3 exists to support **human-reviewed decisions** and **manual
upgrades** only.

------------------------------------------------------------------------

## 2. Authority Boundaries (Hard)

ACv3 MUST:

-   remain **read-only / advisory**
-   remain **deterministic** (replayable outputs for identical inputs)
-   be **fail-closed** on malformed / ambiguous / incomplete inputs
-   produce outputs that are **explainable** and **auditable**

ACv3 MUST NOT:

-   execute transactions
-   modify wallet or node state
-   hold keys or secrets
-   auto-apply patches or upgrades
-   guess missing data
-   introduce black-box ML behavior

------------------------------------------------------------------------

## 3. Determinism Requirements

For any given set of canonical inputs, ACv3 outputs MUST be:

-   bit-for-bit stable for canonical JSON artifacts (where applicable)
-   stable in ordering (no nondeterministic iteration / set ordering)
-   stable in hashing (explicit canonicalization before hashing)

No time-based, random, or environment-dependent behavior is permitted in
the v3 pipeline.

------------------------------------------------------------------------

## 4. Inputs (v3 Observations)

ACv3 accepts **v3 observations** that MUST be:

-   schema-valid (strict)
-   canonicalized (stable ordering, stable normalization)
-   explicitly versioned (v3 contract version markers)

Invalid inputs MUST be rejected **fail-closed** with explicit reason
identifiers.

------------------------------------------------------------------------

## 5. Outputs (Reports + Envelope)

ACv3 outputs include:

1.  **Findings**
    -   deterministic findings derived from observation streams and
        evidence stores
    -   optional drift findings when explicit contracts exist
2.  **Report Artifacts**
    -   canonical JSON report (stable structure)
    -   stable Markdown rendering of the same report content
3.  **Integrity Envelope**
    -   deterministic context hash computed over canonical report
        content
    -   explicit signature status (present/absent/invalid) without
        implied authority

Output formats are contract-defined and MUST NOT change without contract
version discipline.

------------------------------------------------------------------------

## 6. Upgrade Proposals (Mailbox + Validation + Optional Outbox)

ACv3 supports **structured upgrade proposals** as a *human-reviewed mailbox*.

Rules:

- Proposals MUST conform to the v3 schema:
  [`proposals/schema/upgrade_proposal_v3.schema.json`](../../../proposals/schema/upgrade_proposal_v3.schema.json)
- Proposals are **human-reviewed** and submitted via Pull Request into the repository
  `proposals/` mailbox.
- ACv3 MUST NOT auto-apply upgrades, auto-merge proposals, or mutate external systems.

Optional Outbox (artifact emission):

- ACv3 tooling MAY emit sealed proposals into `proposals/outbox/` as deterministic artifacts.
- Outbox emission is **idempotent** when the same bytes already exist.
- If a deterministic filename collision occurs with different bytes, emission MUST fail-closed.
- Outbox emission does not grant execution authority; it is governance artifact production only.

## 7. Implementation Surface (Current Modules)

The v3 implementation surface includes:

-   Canonicalization: `adaptive_core.v3.canonicalize`
-   Evidence window store: `adaptive_core.v3.evidence_store`
-   Findings & analysis: `adaptive_core.v3.analyze`,
    `adaptive_core.v3.findings`
-   Drift detection: `adaptive_core.v3.drift`
-   Correlation & graph utilities: `adaptive_core.v3.correlation`,
    `adaptive_core.v3.graph`
-   Confidence scoring: `adaptive_core.v3.confidence`
-   Guardrails registry: `adaptive_core.v3.guardrails.registry`
-   Reason IDs: `adaptive_core.v3.reason_ids`
-   Report builder/renderers: `adaptive_core.v3.report_builder`
-   Integrity envelope: `adaptive_core.v3.envelope`,
    `adaptive_core.v3.context_hash`
-   Pipeline orchestration: `adaptive_core.v3.pipeline`
-   Cross-node summary (privacy-preserving):
    `adaptive_core.v3.node_summary`
-   Upgrade proposals helpers: `adaptive_core.v3.proposals`

This list is descriptive. The **contract obligations** above are
normative.

------------------------------------------------------------------------

## 8. Versioning Rules

-   Any change that **relaxes** validation, changes canonicalization, or
    alters report structure is a **contract change**.
-   Contract changes MUST be accompanied by:
    -   explicit doc updates to this file
    -   deterministic tests that lock the behavior (regression locks)

------------------------------------------------------------------------

## 9. Out of Scope

The following are explicitly out of scope for ACv3:

-   automated patch delivery
-   auto-remediation
-   autonomous governance
-   wallet UX decisions
-   network consensus modifications

ACv3 produces **advisory intelligence** only.
