# Adaptive Core v3 — Authority Boundaries (Normative)

**Status:** Normative  
**Scope:** defines what ACv3 is allowed to do, and what it is forbidden to do.

This document is **normative**. If code or any other documentation conflicts with this file, **this file wins**.

---

## 1. Boundary Statement

Adaptive Core v3 (“ACv3”) is a **read-only Upgrade Oracle**.

It exists to:
- observe
- summarize
- report

It does **not** exist to:
- control
- execute
- modify
- authorize

---

## 2. Hard Prohibitions (Deny-by-Default)

ACv3 MUST NOT:

### 2.1 Transaction / Key Authority
- generate, store, or access private keys
- access seed phrases or mnemonic material
- sign transactions
- broadcast transactions
- construct spend outputs
- alter recipient addresses or amounts

### 2.2 Wallet / Node State Authority
- change wallet state, balances, UTXO sets, mempool policies
- change node configuration or runtime parameters
- trigger shutdowns, quarantines, or lockdown actions
- modify rule-sets in other shield layers automatically

### 2.3 Upgrade / Patch Authority
- auto-apply patches
- auto-update shield layers
- change guardrail registries without explicit human-managed releases
- silently accept non-v3 input shapes

### 2.4 I/O Authority (Implicit Effects)
- perform disk persistence implicitly
- perform network I/O implicitly
- phone-home telemetry implicitly
- load external resources implicitly (remote rules, feeds, models)

Any persistence or networking must be explicitly designed as a separate, opt-in integration layer and must be fail-closed.

---

## 3. Allowed Powers (Explicit, Minimal)

ACv3 MAY:

- strictly validate inputs (fail-closed with reason codes)
- canonicalize inputs deterministically
- maintain bounded in-memory counters (hot window)
- compute deterministic findings (including drift findings when explicit contracts are supplied)
- render reports deterministically (canonical JSON + stable Markdown)
- produce an integrity envelope (hash + explicit signature status)
- provide privacy-preserving cross-node summaries (aggregated counts only)

---

## 4. Human Review Requirement

ACv3 outputs are advisory.

Human review is required before:
- taking defensive actions
- adjusting thresholds or policies in other layers
- deploying upgrades or patches

ACv3 may recommend actions, but it MUST NOT be wired as an autonomous authority.

---

## 5. Integration Rule (No Hidden Authority)

Downstream components MUST treat ACv3 output as:
- **input to decision-making**, not an execution command.

If any integration attempts to interpret ACv3 output as a command, that integration is violating this boundary contract.

---

## 6. Security Posture

ACv3 must be safe under:
- malformed inputs
- adversarial meta payloads
- attempted schema confusion
- attempted “authority escalation” via report fields

Fail-closed behavior is mandatory.
