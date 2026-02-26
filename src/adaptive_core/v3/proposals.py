from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

from .guardrails.registry import load_registry
from .reason_ids import ReasonId


# Domain + action are now first-class, deny-by-default fields.
_ALLOWED_DOMAINS = {
    "SECURITY_THRESHOLDS",
    "DETECTION_RULES",
    "EVIDENCE_REQUIREMENTS",
    "ENFORCEMENT",
}

_ALLOWED_ACTIONS = {
    "INCREASE_THRESHOLD",
    "ADD_RULE",
    "TIGHTEN_EVIDENCE",
    "STRENGTHEN_ENFORCEMENT",
}


_ALLOWED_ROOT_KEYS = {
    "v",
    "proposal_id",
    "domain",
    "action",
    "target",
    "created_utc",
    "summary",
    "changes",
    "evidence",
    "guardrails",
    "guardrails_ref",
    "proposal_hash",
}

_ALLOWED_TARGET_KEYS = {"component", "version"}
_ALLOWED_CHANGE_KEYS = {"change_id", "type", "detail"}

# Keep existing allowed change types unless you intentionally want a breaking change.
# If you want to forbid destructive removals, remove "remove" here AND update schema + tests.
_ALLOWED_CHANGE_TYPES = {"add", "modify", "deprecate", "remove"}


@dataclass(frozen=True, slots=True)
class ProposalValidationResult:
    canonical: Dict[str, Any]
    computed_hash: str


def _require_str(m: Mapping[str, Any], key: str) -> str:
    if key not in m:
        raise ValueError(f"{ReasonId.AC_V3_MISSING_FIELD.value}: missing {key!r}")
    v = m[key]
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"{ReasonId.AC_V3_TYPE_INVALID.value}: {key!r} must be non-empty str")
    return v.strip()


def _require_timestamp_z(value: str) -> str:
    if not value.endswith("Z"):
        raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_TIMESTAMP_INVALID.value}: created_utc must end with 'Z'")
    try:
        datetime.fromisoformat(value[:-1])
    except ValueError as e:
        raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_TIMESTAMP_INVALID.value}: invalid ISO8601 timestamp") from e
    return value


def _require_exact_keys(obj: Mapping[str, Any], allowed: Iterable[str], ctx: str) -> None:
    extra = sorted(set(obj.keys()) - set(allowed))
    if extra:
        raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: unknown keys in {ctx}: {extra}")


def _repo_root_from_here() -> Path:
    # Walk upward until we find repo root that contains "proposals/"
    here = Path(__file__).resolve()
    for p in [here] + list(here.parents):
        if (p / "proposals").is_dir():
            return p
    raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: repo root not found")


def _canonical_json_bytes(obj: Any) -> bytes:
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return s.encode("utf-8")


def compute_proposal_hash(canonical_without_hash: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json_bytes(canonical_without_hash)).hexdigest()


def _canonicalize_guardrails(guardrails: Optional[Any], guardrails_ref: Optional[Any]) -> Tuple[List[str], Optional[str]]:
    if guardrails is None:
        gids: List[str] = []
    else:
        if not isinstance(guardrails, list):
            raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: 'guardrails' must be list[str]")
        gids = []
        for g in guardrails:
            if not isinstance(g, str) or not g.strip():
                raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: guardrail ids must be non-empty str")
            gids.append(g.strip())

    ref: Optional[str] = None
    if guardrails_ref is not None:
        if not isinstance(guardrails_ref, str) or not guardrails_ref.strip():
            raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: 'guardrails_ref' must be non-empty str")
        ref = guardrails_ref.strip()

    gids = sorted(set(gids))
    return gids, ref


def validate_and_canonicalize_upgrade_proposal(raw: Mapping[str, Any]) -> ProposalValidationResult:
    if not isinstance(raw, Mapping):
        raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: proposal must be an object")

    _require_exact_keys(raw, _ALLOWED_ROOT_KEYS, ctx="proposal")

    v = _require_str(raw, "v")
    if v != "upgrade_proposal_v3":
        raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: bad 'v'")

    proposal_id = _require_str(raw, "proposal_id")
    if " " in proposal_id:
        raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: proposal_id must not contain spaces")

    # New fields (deny-by-default)
    domain = _require_str(raw, "domain")
    if domain not in _ALLOWED_DOMAINS:
        raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: bad domain {domain!r}")

    action = _require_str(raw, "action")
    if action not in _ALLOWED_ACTIONS:
        raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: bad action {action!r}")

    target = raw.get("target")
    if not isinstance(target, Mapping):
        raise ValueError(f"{ReasonId.AC_V3_TYPE_INVALID.value}: 'target' must be object")
    _require_exact_keys(target, _ALLOWED_TARGET_KEYS, ctx="target")
    component = _require_str(target, "component")
    version = _require_str(target, "version")

    created_utc = _require_str(raw, "created_utc")
    created_utc = _require_timestamp_z(created_utc)

    summary = _require_str(raw, "summary")

    changes_any = raw.get("changes")
    if not isinstance(changes_any, list) or not changes_any:
        raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: 'changes' must be non-empty list")

    changes: List[Dict[str, str]] = []
    seen_change_ids: set[str] = set()
    for item in changes_any:
        if not isinstance(item, Mapping):
            raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: change entry must be object")
        _require_exact_keys(item, _ALLOWED_CHANGE_KEYS, ctx="change")
        cid = _require_str(item, "change_id")
        ctype = _require_str(item, "type")
        detail = _require_str(item, "detail")
        if ctype not in _ALLOWED_CHANGE_TYPES:
            raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: bad change.type {ctype!r}")
        if cid in seen_change_ids:
            raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: duplicate change_id {cid!r}")
        seen_change_ids.add(cid)
        changes.append({"change_id": cid, "type": ctype, "detail": detail})

    changes.sort(key=lambda d: d["change_id"])

    evidence = raw.get("evidence")
    if evidence is not None and not isinstance(evidence, dict):
        raise ValueError(f"{ReasonId.AC_V3_TYPE_INVALID.value}: 'evidence' must be object if present")

    gids, gref = _canonicalize_guardrails(raw.get("guardrails"), raw.get("guardrails_ref"))

    registry = load_registry()
    registry.require_all(gids)

    proposal_hash = _require_str(raw, "proposal_hash")
    if len(proposal_hash) != 64 or any(c not in "0123456789abcdef" for c in proposal_hash):
        raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_HASH_INVALID.value}: proposal_hash must be 64 lowercase hex chars")

    canonical: Dict[str, Any] = {
        "v": v,
        "proposal_id": proposal_id,
        "domain": domain,
        "action": action,
        "target": {"component": component, "version": version},
        "created_utc": created_utc,
        "summary": summary,
        "changes": changes,
        "evidence": dict(evidence) if isinstance(evidence, dict) else {},
        "guardrails": gids,
        "guardrails_ref": gref if gref is not None else "",
        "proposal_hash": proposal_hash,
    }

    without_hash = dict(canonical)
    without_hash.pop("proposal_hash", None)
    computed = compute_proposal_hash(without_hash)

    if proposal_hash != computed:
        raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_HASH_INVALID.value}: expected {computed} got {proposal_hash}")

    return ProposalValidationResult(canonical=canonical, computed_hash=computed)


def load_json_file(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: invalid json {path}") from e
    if not isinstance(data, dict):
        raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: json root must be object {path}")
    return data


def validate_inbox() -> None:
    root = _repo_root_from_here()
    inbox = root / "proposals" / "inbox"
    if not inbox.exists() or not inbox.is_dir():
        raise ValueError(f"{ReasonId.AC_V3_PROPOSAL_INVALID.value}: proposals/inbox missing")

    for p in sorted(inbox.glob("*.json")):
        raw = load_json_file(p)
        validate_and_canonicalize_upgrade_proposal(raw)
