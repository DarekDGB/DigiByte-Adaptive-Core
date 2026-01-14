# Adaptive Core v3 — Documentation Index

This index defines the **authoritative documentation set** for Adaptive Core v3.

Adaptive Core v3 is a **read-only Upgrade Oracle**.  
It observes, validates, summarizes, and reports — nothing more.

---

## 1. Orientation

- **README.md**  
  High-level purpose, guarantees, and non-goals.

- **ADAPTIVE_CORE_V3_ARCHITECTURE_DIAGRAMS.md**  
  Visual architecture only (no duplicated prose).

---

## 2. Authority & Contract

- **AUTHORITY_BOUNDARIES.md**  
  What Adaptive Core v3 is allowed and forbidden to do.

- **CONTRACT.md**  
  Normative behavioral contract. Overrides diagrams and prose.

---

## 3. Guardrails & Reasoning

- **GUARDRAILS.md**  
  Machine-enforced guardrail registry (fail-closed).

- **REASON_IDS.md**  
  Canonical error and decision identifiers.

---

## 4. Security Model

- **SECURITY.md**  
  Threat model, assumptions, and non-goals.

---

## 5. Evidence & Analysis

- **EVIDENCE_STORE.md**  
  Hot-window deterministic evidence aggregation.

- **CONFIDENCE_MODEL.md**  
  Confidence scoring rules and bounds.

- **DRIFT_RADAR.md**  
  Drift detection with explicit contracts only.

- **CORRELATION.md**  
  Optional correlation logic (disabled by default).

---

## 6. Reporting & Output

- **REPORT_FORMAT.md**  
  Canonical JSON and Markdown report formats.

- **PIPELINE_USAGE.md**  
  End-to-end execution flow for v3 pipeline.

- **NODE_SUMMARY.md**  
  Privacy-preserving cross-node aggregation.

---

## 7. Precedence Rules

1. Code
2. CONTRACT.md
3. This index
4. Other documentation

Anything not explicitly permitted is forbidden by default.

---

© 2025 DarekDGB
