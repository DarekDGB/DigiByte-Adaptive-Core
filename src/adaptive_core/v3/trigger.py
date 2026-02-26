from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .proposals import build_upgrade_proposal_v3
from .outbox import emit_upgrade_proposal_v3_to_outbox


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def maybe_propose_upgrade_from_findings(
    *,
    findings: List[Dict[str, Any]],
    drift_threshold: float,
    proposal_id: str,
    component: str,
    version: str,
    outbox_dir: Path,
) -> Optional[Dict[str, Any]]:
    """
    Deterministic advisory trigger.

    If any finding contains drift_score >= drift_threshold,
    emit an upgrade_proposal_v3 artifact and return canonical proposal.

    Otherwise return None.
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
        "target": {
            "component": component,
            "version": version,
        },
        "created_utc": _utc_now_iso(),
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

    emit_upgrade_proposal_v3_to_outbox(
        sealed,
        outbox_dir=outbox_dir,
    )

    return sealed
