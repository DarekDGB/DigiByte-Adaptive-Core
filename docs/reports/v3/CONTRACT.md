# Adaptive Core v3 --- CONTRACT (Normative)

**Status:** Normative • Contract-Locking Document\
**Scope:** `adaptive_core.v3.*` (read-only upgrade oracle)

This document is **normative**. If other docs diverge, **this file
wins**.\
If **code** diverges from this contract, that is a **bug** and must be
fixed with a regression test.

------------------------------------------------------------------------

## 1. Purpose

Adaptive Core v3 ("ACv3") is the **Upgrade Oracle** in the DigiByte
Quantum Shield v4 ecosystem.

It ingests **strict, canonicalized, v3-shaped observations** and
produces **deterministic advisory outputs**:

-   evidence counters (bounded hot window)
-   findings (including optional drift findings when explicit contracts
    are provided)
-   upgrade reports (canonical JSON + stable Markdown)
-   integrity envelope (`report_hash` plus explicit local
    `classical_signature` and `pqc_signature` status metadata)

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

### 2.1 Shield v4 compatibility boundary

ACv3 MUST NOT:

-   parse or verify Shield signature bundles
-   select or reuse Shield trust-registry keys
-   interpret Shield evidence as approval or execution authority
-   approve, override, downgrade, bypass, or rescue a Shield outcome
-   reuse Q-ID identity keys as Shield decision-evidence keys

Shield evidence requires `classical-ed25519 + ml-dsa`. Optional `fn-dsa` evidence uses Falcon-1024 under `fips206-draft-falcon1024-v1`; it is optional draft-profile evidence, not final FIPS 206 proof. ACv3 does not enforce this cryptographic policy and cannot make FN-DSA required or use it as rescue logic.

AdamantineOS independently verifies Shield evidence under verifier-controlled policy and remains the authoritative, fail-closed final policy and execution boundary.

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
    -   stable human-readable Markdown subset and summary derived from
        the same report object
3.  **Integrity Envelope**
    -   in-memory `ReportEnvelopeV3` retains the exact `canonical_json`
        string alongside its hash and status metadata
    -   deterministic `report_hash` computed over canonical report
        JSON
    -   local `classical_signature` and `pqc_signature` status metadata
        using exactly `ABSENT`, `PRESENT`, or `UNSUPPORTED`
    -   no signature bytes, signature verification, or implied authority

`ReportEnvelopeV3.to_dict()` emits `report_hash`, `classical_signature`, and `pqc_signature`; `canonical_json` remains observable on the envelope object and is already returned separately by the pipeline.

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
-   Integrity envelope: `adaptive_core.v3.envelope`
-   Event context hashing: `adaptive_core.v3.context_hash`
-   AdamantineOS advisory exporter:
    `adaptive_core.v3.integration.adamantine`
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
-   Shield cryptographic verification or Shield key management

ACv3 produces **advisory intelligence** only.
