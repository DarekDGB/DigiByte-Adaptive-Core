# CONFIDENCE_MODEL (v3)

## Purpose

This document describes how Adaptive Core v3 computes a **confidence score** and
applies a **confidence threshold** for upgrade recommendations.

Implementation: `adaptive_core.v3.confidence`

v3 confidence is **advisory** only:
- it never executes changes
- it never upgrades layers automatically
- it is used to gate report recommendations

---

## Inputs

v3 confidence is derived from:

- the deterministic evidence snapshot (counts, distribution)
- findings presence / severity (if applicable)
- capability flags (what the system claims it can observe)
- optional drift contracts (when drift analysis is enabled)

The exact scoring function is defined in code and is normative.

---

## Outputs

- `confidence_score`: float in **[0.0, 1.0]**
- `meets_threshold`: boolean, computed as `confidence_score >= confidence_threshold`

---

## Guardrails

1. **No randomness**: confidence must be deterministic for the same inputs.
2. **Clamped range**: score must remain within [0.0, 1.0].
3. **Explicit threshold**: threshold must be provided to the pipeline.
4. **Fail-closed**: missing required inputs (in code paths that require them) must raise with a reason id.

---

## Design intent

- Low evidence â low confidence.
- Consistent evidence from multiple sources â higher confidence.
- Drift contracts provided and validated â higher confidence (when enabled).
- Confidence is a signal for humans and downstream systems to prioritize review.

---

## Recommended threshold defaults (policy)

These are *policy suggestions* (not code authority):

- Conservative / high assurance: **0.85 â 0.95**
- Balanced review pipeline: **0.70 â 0.85**
- Experimental / lab environment: **0.50 â 0.70**

Final thresholds must be set by the consuming project (shield integration).
