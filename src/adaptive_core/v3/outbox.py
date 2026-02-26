from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping

from .proposals import validate_and_canonicalize_upgrade_proposal
from .reason_ids import ReasonId


def _canonical_json_text(obj: Any) -> str:
    # Stable output for diffs + reproducibility
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def upgrade_proposal_v3_outbox_filename(canonical: Mapping[str, Any]) -> str:
    proposal_id = str(canonical["proposal_id"])
    proposal_hash = str(canonical["proposal_hash"])
    # Deterministic, filesystem-safe, low collision risk
    return f"{proposal_id}.{proposal_hash[:12]}.upgrade_proposal_v3.json"


def emit_upgrade_proposal_v3_to_outbox(
    sealed: Mapping[str, Any],
    *,
    outbox_dir: Path,
) -> Path:
    """
    Emit a sealed upgrade_proposal_v3 into an outbox directory.

    - Fail-closed: validates and canonicalizes first.
    - Deterministic filename derived from proposal_id + proposal_hash prefix.
    - Idempotent: if file exists with same bytes, return path.
    - If file exists with different content: fail closed.
    """
    if not isinstance(outbox_dir, Path):
        raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: outbox_dir must be Path")

    if not outbox_dir.exists() or not outbox_dir.is_dir():
        raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: outbox_dir does not exist: {outbox_dir}")

    canonical = validate_and_canonicalize_upgrade_proposal(sealed).canonical
    filename = upgrade_proposal_v3_outbox_filename(canonical)
    path = outbox_dir / filename

    payload = _canonical_json_text(canonical).encode("utf-8")

    if path.exists():
        existing = path.read_bytes()
        if existing == payload:
            return path
        raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: outbox collision: {path.name}")

    path.write_bytes(payload)
    return path
