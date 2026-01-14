# Adaptive Core — Documentation Index

This repository contains **two parallel lines**:

- **v2 (Legacy Learning Engine):** historical adaptive/learning engine and immune report logic.
- **v3 (Upgrade Oracle):** deterministic, fail-closed **reporting/oracle** that produces human-reviewed upgrade reports.
  - **No execution authority**
  - **No keys**
  - **No silent fallback**

---

## v3 Documentation (Current)

Start here:

- [v3 Overview](v3/README.md)
- [v3 Guardrails Registry](v3/GUARDRAILS.md)

Planned / to be added next (in order):

- `v3/AUTHORITY_BOUNDARIES.md`
- `v3/CONTRACT.md`
- `v3/REASON_IDS.md`
- `v3/REPORT_FORMAT.md`
- `v3/EVIDENCE_STORE.md`
- `v3/CONFIDENCE_MODEL.md`
- `v3/DRIFT_RADAR.md`
- `v3/NODE_SUMMARY.md`
- `v3/CORRELATION.md`
- `v3/PIPELINE_USAGE.md`

---

## v2 Documentation (Legacy)

Start here:

- [v2 Overview](v2/README.md)
- v2 report docs:
  - `v2/reports/immune-report-schema.md`
  - `v2/reports/qri-scoring.md`
  - `v2/reports/reinforcement-learning-rules.md`

---

## Scope truth

If any future docs conflict with **code** for v3, then:

1. **Tests/contracts win**
2. Then **code**
3. Then docs

Docs must never invent authority that the code does not have.
