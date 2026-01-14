from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Dict, List

from .analyze import AnalyzeConfig, generate_findings
from .confidence import compute_confidence, load_confidence_weights
from .evidence_store import EvidenceSnapshot
from .guardrails.registry import load_registry
from .reason_ids import ReasonId
from .report_models import CapabilitiesV3, UpgradeReportV3


DEFAULT_CONFIDENCE_THRESHOLD = 0.60


def _json_dumps_stable(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def build_upgrade_report(
    *,
    report_id: str,
    target_layers: List[str],
    snapshot: EvidenceSnapshot,
    capabilities: CapabilitiesV3,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> UpgradeReportV3:
    """
    Build a deterministic v3 report (MD + JSON can be derived from this object).

    Guardrail enforcement:
    - All guardrail IDs must exist in registry, otherwise fail-closed.
    """
    if not report_id or not isinstance(report_id, str):
        raise ValueError(f"{ReasonId.AC_V3_REPORT_INVALID.value}: report_id")
    if not target_layers or any((not isinstance(x, str) or not x.strip()) for x in target_layers):
        raise ValueError(f"{ReasonId.AC_V3_REPORT_INVALID.value}: target_layers")

    registry = load_registry()
    weights = load_confidence_weights()

    findings_objs = generate_findings(snapshot, AnalyzeConfig())
    findings: List[Dict[str, Any]] = [asdict(f) for f in findings_objs]

    # Evidence summary is deterministic
    evidence = {
        "total_events": snapshot.total_events,
        "by_source_layer": dict(sorted(snapshot.by_source_layer.items())),
        "by_event_type": dict(sorted(snapshot.by_event_type.items())),
        "by_upstream_reason_id": dict(sorted(snapshot.by_upstream_reason_id.items())),
    }

    # Compute deterministic confidence (bounded inputs)
    total = snapshot.total_events if snapshot.total_events > 0 else 1
    # Recurrence ratio: max reason-id ratio (if any)
    max_reason_ratio = 0.0
    if snapshot.by_upstream_reason_id:
        max_reason_ratio = max(snapshot.by_upstream_reason_id.values()) / total

    # Average severity proxy: use max finding severity if present (still deterministic)
    avg_sev = max((f.severity for f in findings_objs), default=0.0)

    # Reproducibility proxy (Step 4): 0.5 if we have at least one finding, else 0.0
    reproducibility = 0.5 if findings_objs else 0.0

    # Cross-layer impact proxy: bounded by number of target layers (Step 4 minimal)
    cross_layer_impact = min(1.0, len(target_layers) / 5.0)

    confidence = compute_confidence(
        recurrence_ratio=max_reason_ratio,
        avg_severity=avg_sev,
        reproducibility=reproducibility,
        cross_layer_impact=cross_layer_impact,
        weights=weights,
    )

    # Guardrails: union from findings (deterministic)
    guardrails_set = set()
    for f in findings_objs:
        guardrails_set.update(f.guardrails)
    guardrails = sorted(guardrails_set)

    # Validate guardrails against registry (fail-closed)
    registry.require_all(guardrails)
    guardrail_titles = registry.titles_for(guardrails)

    # If low confidence: do NOT generate upgrade actions
    if confidence < confidence_threshold:
        return UpgradeReportV3(
            report_id=report_id,
            report_type="SIGNAL_COLLECTION_NOTICE",
            target_layers=sorted(target_layers),
            evidence=evidence,
            findings=findings,
            guardrails=guardrails,
            guardrail_titles=guardrail_titles,
            confidence=round(confidence, 6),
            confidence_breakdown={
                "recurrence_ratio": round(max_reason_ratio, 6),
                "avg_severity": round(avg_sev, 6),
                "reproducibility": round(reproducibility, 6),
                "cross_layer_impact": round(cross_layer_impact, 6),
            },
            capabilities=capabilities,
            recommended_actions=[
                "Collect more evidence for recurring reason codes and anomalies.",
                "Add detectors or instrumentation in upstream layers to increase signal quality.",
            ],
            required_tests=[],
            exit_criteria=[
                "Confidence must meet threshold before emitting an Upgrade Report.",
                "All evidence and findings must remain deterministic and reproducible.",
            ],
            forbidden_actions=[
                "Do not relax validation to increase event acceptance.",
                "Do not apply any code changes based on low-confidence notices.",
            ],
        )

    # High confidence: emit upgrade guidance (still advisory-only)
    return UpgradeReportV3(
        report_id=report_id,
        report_type="UPGRADE_REPORT",
        target_layers=sorted(target_layers),
        evidence=evidence,
        findings=findings,
        guardrails=guardrails,
        guardrail_titles=guardrail_titles,
        confidence=round(confidence, 6),
        confidence_breakdown={
            "recurrence_ratio": round(max_reason_ratio, 6),
            "avg_severity": round(avg_sev, 6),
            "reproducibility": round(reproducibility, 6),
            "cross_layer_impact": round(cross_layer_impact, 6),
        },
        capabilities=capabilities,
        recommended_actions=[
            "Harden validation/canonicalization at the boundary where the spike occurs.",
            "Eliminate ambiguous defaults; require explicit inputs or fail closed.",
            "Add negative tests to reproduce the observed failure mode and lock regression.",
        ],
        required_tests=[
            "Add a negative test that fails on current behavior and passes after the fix.",
            "Add a regression lock referencing this report_id.",
        ],
        exit_criteria=[
            "New tests MUST fail on the prior version and pass after the fix.",
            "Coverage must not regress (≥ project threshold).",
            "No silent fallbacks; all rejects must emit explicit reason codes.",
        ],
        forbidden_actions=[
            "Do not relax validation rules.",
            "Do not introduce silent defaults.",
            "Do not auto-apply changes; human review is mandatory.",
        ],
    )


def render_report_json(report: UpgradeReportV3) -> str:
    return _json_dumps_stable(asdict(report))


def render_report_md(report: UpgradeReportV3) -> str:
    # Simple deterministic MD rendering (no timestamps, no randomness)
    lines: List[str] = []
    lines.append("# 🔷 ADAPTIVE CORE — UPGRADE REPORT v3")
    lines.append("")
    lines.append(f"**Report ID:** {report.report_id}")
    lines.append(f"**Type:** {report.report_type}")
    lines.append(f"**Target Layers:** {', '.join(report.target_layers)}")
    lines.append("")
    lines.append("## 🧩 Capabilities")
    lines.append(f"- Envelope: {report.capabilities.envelope}")
    lines.append(f"- Correlation: {report.capabilities.correlation}")
    lines.append(f"- Archival: {report.capabilities.archival}")
    lines.append(f"- Telemetry: {report.capabilities.telemetry}")
    lines.append("")
    lines.append("## 📌 Evidence Summary")
    lines.append(f"- Total events: {report.evidence['total_events']}")
    lines.append("")
    lines.append("## 🛡️ Guardrails Triggered")
    for gid in report.guardrails:
        title = report.guardrail_titles.get(gid, "")
        lines.append(f"- **{gid}** — {title}")
    lines.append("")
    lines.append("## 📊 Confidence")
    lines.append(f"**Score:** {report.confidence}")
    for k in sorted(report.confidence_breakdown.keys()):
        lines.append(f"- {k}: {report.confidence_breakdown[k]}")
    lines.append("")
    lines.append("## ✅ Recommended Actions")
    for a in report.recommended_actions:
        lines.append(f"- {a}")
    lines.append("")
    lines.append("## 🧪 Required Tests")
    if report.required_tests:
        for t in report.required_tests:
            lines.append(f"- {t}")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("## ✅ Exit Criteria")
    for x in report.exit_criteria:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## ⛔ Forbidden Actions")
    for x in report.forbidden_actions:
        lines.append(f"- {x}")
    lines.append("")
    return "\n".join(lines)
