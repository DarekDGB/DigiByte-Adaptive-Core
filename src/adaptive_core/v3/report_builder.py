from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from .analyze import AnalyzeConfig, generate_findings
from .confidence import compute_confidence, load_confidence_weights
from .correlation import CorrelationSnapshot, generate_correlation_findings
from .drift import LayerContract, detect_contract_drift
from .evidence_store import EvidenceSnapshot
from .findings import FindingV3
from .graph import render_drift_dot
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
    # Step 8:
    drift_contracts: Optional[List[LayerContract]] = None,
    include_drift_graph: bool = False,
    # Step 10:
    correlation_snapshot: Optional[CorrelationSnapshot] = None,
    include_correlation: bool = False,
) -> UpgradeReportV3:
    """
    Build a deterministic v3 report.

    - Evidence findings come from counters (generate_findings)
    - Drift findings come from explicit LayerContract inputs (detect_contract_drift)
    - Correlation findings come from explicit CorrelationSnapshot (generate_correlation_findings)
    - Guardrails are validated against registry (fail-closed)
    """
    if not report_id or not isinstance(report_id, str):
        raise ValueError(f"{ReasonId.AC_V3_REPORT_INVALID.value}: report_id")
    if not target_layers or any((not isinstance(x, str) or not x.strip()) for x in target_layers):
        raise ValueError(f"{ReasonId.AC_V3_REPORT_INVALID.value}: target_layers")
    if drift_contracts is not None and not isinstance(drift_contracts, list):
        raise ValueError(f"{ReasonId.AC_V3_REPORT_INVALID.value}: drift_contracts must be list or None")
    if correlation_snapshot is not None and not isinstance(correlation_snapshot, CorrelationSnapshot):
        raise ValueError(f"{ReasonId.AC_V3_REPORT_INVALID.value}: correlation_snapshot must be CorrelationSnapshot or None")
    if include_correlation and correlation_snapshot is None:
        raise ValueError(f"{ReasonId.AC_V3_REPORT_INVALID.value}: include_correlation requires correlation_snapshot")

    registry = load_registry()
    weights = load_confidence_weights()

    # Evidence findings (from hot-window counters)
    evidence_findings: List[FindingV3] = generate_findings(snapshot, AnalyzeConfig())

    # Drift findings (explicit inputs only — no guessing)
    drift_findings: List[FindingV3] = []
    if drift_contracts:
        drift_findings = detect_contract_drift(drift_contracts)

    # Correlation findings (explicit snapshot only — summaries, no raw events)
    corr_findings: List[FindingV3] = []
    if include_correlation and correlation_snapshot is not None:
        corr_findings = generate_correlation_findings(correlation_snapshot)

    # Merge findings deterministically: sort by finding_id
    all_findings: List[FindingV3] = sorted(
        (evidence_findings + drift_findings + corr_findings),
        key=lambda f: f.finding_id,
    )
    findings_dicts: List[Dict[str, Any]] = [asdict(f) for f in all_findings]

    # Evidence summary is deterministic
    evidence = {
        "total_events": snapshot.total_events,
        "by_source_layer": dict(sorted(snapshot.by_source_layer.items())),
        "by_event_type": dict(sorted(snapshot.by_event_type.items())),
        "by_upstream_reason_id": dict(sorted(snapshot.by_upstream_reason_id.items())),
        "drift_contracts_provided": 0 if not drift_contracts else len(drift_contracts),
        "drift_findings": len(drift_findings),
        "correlation_enabled": bool(include_correlation and correlation_snapshot is not None),
        "correlation_nodes": 0 if correlation_snapshot is None else correlation_snapshot.total_nodes,
        "correlation_findings": len(corr_findings),
    }

    total = snapshot.total_events if snapshot.total_events > 0 else 1

    # recurrence ratio: max reason-id ratio (if any)
    max_reason_ratio = 0.0
    if snapshot.by_upstream_reason_id:
        max_reason_ratio = max(snapshot.by_upstream_reason_id.values()) / total

    # severity proxy: max finding severity if present
    max_sev = max((float(f.severity) for f in all_findings), default=0.0)

    # reproducibility proxy:
    # - 1.0 if any finding includes a reason_id evidence key
    # - 0.5 if there are findings but no reason_id
    # - 0.0 if none
    if not all_findings:
        reproducibility = 0.0
    elif any(isinstance(f.evidence, dict) and "reason_id" in f.evidence for f in all_findings):
        reproducibility = 1.0
    else:
        reproducibility = 0.5

    # cross-layer impact: driven by drift findings presence and number of target layers
    # deterministic: bounded in [0,1]
    drift_signal = 0.0 if not drift_findings else min(1.0, len(drift_findings) / 5.0)
    layer_signal = min(1.0, len(target_layers) / 5.0)
    corr_signal = 0.0 if not corr_findings else min(1.0, len(corr_findings) / 5.0)
    cross_layer_impact = max(drift_signal, layer_signal, corr_signal)

    confidence = compute_confidence(
        recurrence_ratio=max_reason_ratio,
        avg_severity=max_sev,
        reproducibility=reproducibility,
        cross_layer_impact=cross_layer_impact,
        weights=weights,
    )

    # Guardrails: union from all findings (deterministic)
    guardrails_set = set()
    for f in all_findings:
        guardrails_set.update(f.guardrails)
    guardrails = sorted(guardrails_set)

    # Validate guardrails against registry (fail-closed)
    registry.require_all(guardrails)
    guardrail_titles = registry.titles_for(guardrails)

    drift_dot: Optional[str] = None
    if include_drift_graph and drift_findings:
        drift_dot = render_drift_dot(drift_findings)

    confidence_breakdown = {
        "recurrence_ratio": round(max_reason_ratio, 6),
        "max_severity": round(max_sev, 6),
        "reproducibility": round(reproducibility, 6),
        "cross_layer_impact": round(cross_layer_impact, 6),
    }

    if confidence < confidence_threshold:
        return UpgradeReportV3(
            report_id=report_id,
            report_type="SIGNAL_COLLECTION_NOTICE",
            target_layers=sorted(target_layers),
            evidence=evidence,
            findings=findings_dicts,
            guardrails=guardrails,
            guardrail_titles=guardrail_titles,
            confidence=round(confidence, 6),
            confidence_breakdown=confidence_breakdown,
            capabilities=capabilities,
            drift_dot=drift_dot,
            recommended_actions=[
                "Collect more evidence for recurring reason codes and anomalies.",
                "If drift is suspected, provide LayerContract inputs for Drift Radar.",
                "If widespread issues are suspected, provide CorrelationSnapshot (summaries only).",
            ],
            required_tests=[],
            exit_criteria=[
                "Confidence must meet threshold before emitting an Upgrade Report.",
                "All outputs must remain deterministic and reproducible.",
            ],
            forbidden_actions=[
                "Do not relax validation to increase acceptance.",
                "Do not apply code changes based on low-confidence notices.",
            ],
        )

    return UpgradeReportV3(
        report_id=report_id,
        report_type="UPGRADE_REPORT",
        target_layers=sorted(target_layers),
        evidence=evidence,
        findings=findings_dicts,
        guardrails=guardrails,
        guardrail_titles=guardrail_titles,
        confidence=round(confidence, 6),
        confidence_breakdown=confidence_breakdown,
        capabilities=capabilities,
        drift_dot=drift_dot,
        recommended_actions=[
            "Harden validation/canonicalization at boundaries where spikes occur.",
            "Resolve contract drift by aligning assumptions across layers (fail-closed).",
            "If correlation indicates widespread issues, treat as global risk and prioritize fixes.",
            "Add negative tests and regression locks referencing this report_id.",
        ],
        required_tests=[
            "Add a negative test that fails before the fix and passes after.",
            "Add a regression lock referencing this report_id.",
        ],
        exit_criteria=[
            "New tests MUST fail on prior version and pass after fix.",
            "Coverage must not regress (≥ project threshold).",
            "No silent fallbacks; explicit reason codes required.",
        ],
        forbidden_actions=[
            "Do not relax validation rules.",
            "Do not introduce silent defaults.",
            "Do not auto-apply changes; human review is mandatory.",
        ],
    )


def render_report_json(report: UpgradeReportV3) -> str:
    # JSON stable ordering
    return _json_dumps_stable(asdict(report))


def render_report_md(report: UpgradeReportV3) -> str:
    # Deterministic MD rendering (no timestamps)
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
    lines.append(f"- Total events: {report.evidence.get('total_events')}")
    lines.append(f"- Drift contracts provided: {report.evidence.get('drift_contracts_provided')}")
    lines.append(f"- Drift findings: {report.evidence.get('drift_findings')}")
    lines.append(f"- Correlation enabled: {report.evidence.get('correlation_enabled')}")
    lines.append(f"- Correlation nodes: {report.evidence.get('correlation_nodes')}")
    lines.append(f"- Correlation findings: {report.evidence.get('correlation_findings')}")
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
    lines.append("## 🔍 Findings")
    if not report.findings:
        lines.append("_No findings in this window._")
    else:
        for f in report.findings:
            lines.append(f"- `{f.get('finding_id')}` — {f.get('title')}")
    lines.append("")

    if report.drift_dot:
        lines.append("## 🧭 Drift Radar Graph (DOT)")
        lines.append("```dot")
        lines.append(report.drift_dot)
        lines.append("```")
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
