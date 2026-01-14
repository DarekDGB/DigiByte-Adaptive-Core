from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional


@dataclass(frozen=True, slots=True)
class CapabilitiesV3:
    envelope: Literal["ABSENT", "PRESENT"]
    correlation: Literal["OFF", "ON"]
    archival: Literal["OFF", "ON"]
    telemetry: Literal["OFF", "ON"]


@dataclass(frozen=True, slots=True)
class UpgradeReportV3:
    report_id: str
    report_type: Literal["UPGRADE_REPORT", "SIGNAL_COLLECTION_NOTICE"]
    target_layers: List[str]

    evidence: Dict[str, Any]
    findings: List[Dict[str, Any]]

    guardrails: List[str]  # AMG IDs
    guardrail_titles: Dict[str, str]  # derived from registry

    confidence: float
    confidence_breakdown: Dict[str, float]

    capabilities: CapabilitiesV3

    # NEW in Step 8: optional drift visualization (deterministic text)
    drift_dot: Optional[str]

    recommended_actions: List[str]
    required_tests: List[str]
    exit_criteria: List[str]
    forbidden_actions: List[str]
