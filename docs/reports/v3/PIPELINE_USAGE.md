# PIPELINE_USAGE (v3)

## Purpose

This document explains how to run the **Adaptive Core v3 pipeline** and interpret outputs.

Entry point: `adaptive_core.v3.pipeline.run_v3_pipeline`

---

## Inputs

Required:

- `report_id: str`
- `target_layers: list[str]`
- `snapshot: EvidenceSnapshot`
- `confidence_threshold: float`
- `capabilities: CapabilitiesV3`

Optional:

- `drift_contracts: list[LayerContract] | None`
- `include_drift_graph: bool`

---

## Example (conceptual)

1. Canonicalize raw observations into `ObservedEventV3` + `context_hash`
2. Add them to `EvidenceStoreV3`
3. Take a deterministic `EvidenceSnapshot`
4. Run the pipeline to build a report + envelope

---

## Outputs

- `UpgradeReportV3` — structured report object
- `canonical_json` — stable renderer output
- `markdown` — stable renderer output
- `ReportEnvelopeV3` — integrity envelope with SHA-256 hash and signature status fields

---

## Operational guidance

- Treat reports as **advisory** artifacts for human review.
- Store canonical JSON as the audit artifact.
- Store the envelope hash in logs / immutable storage for later verification.
- Do not enable drift radar unless you provide explicit contracts.

---

## Failure behavior

- Canonicalization failures raise with `ReasonId` codes.
- Envelope creation fails if canonical_json is missing/invalid or signature status is invalid.
- No silent defaults beyond what is explicitly documented in each module.
