from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .outbox import emit_upgrade_proposal_v3_to_outbox
from .proposals import build_upgrade_proposal_v3


def maybe_propose_upgrade_from_findings(
    *,
    findings: List[Dict[str, Any]],
    drift_threshold: float,
    proposal_id: str,
    component: str,
    version: str,
    created_utc: str,
    outbox_dir: Path,
) -> Optional[Dict[str, Any]]:
    """
    Deterministic advisory trigger (human-only apply).

    If any finding contains drift_score >= drift_threshold,
    emit a sealed upgrade_proposal_v3 artifact into outbox and return the canonical proposal.
    Otherwise return None.

    created_utc is injected to preserve determinism (no clock reads).
    """
    triggered = False
    max_drift = 0.0

    for f in findings:
        drift = float(f.get("drift_score", 0.0))
        if drift >= drift_threshold:
            triggered = True
        if drift > max_drift:
            max_drift = drift

    if not triggered:
        return None

    raw = {
        "v": "upgrade_proposal_v3",
        "proposal_id": proposal_id,
        "domain": "SECURITY_THRESHOLDS",
        "action": "INCREASE_THRESHOLD",
        "target": {"component": component, "version": version},
        "created_utc": created_utc,
        "summary": f"Detected drift_score {max_drift:.4f} >= threshold {drift_threshold:.4f}.",
        "changes": [
            {
                "change_id": "AUTO-DRIFT-001",
                "type": "modify",
                "detail": "Recommend increasing threshold due to sustained drift detection.",
            }
        ],
        "evidence": {},
        "guardrails": ["AMG-001"],
        "guardrails_ref": "docs/ADAPTIVE_CORE_GUARDRAILS.md",
        "proposal_hash": "",
    }

    sealed = build_upgrade_proposal_v3(raw)
    emit_upgrade_proposal_v3_to_outbox(sealed, outbox_dir=outbox_dir)
    return sealed
