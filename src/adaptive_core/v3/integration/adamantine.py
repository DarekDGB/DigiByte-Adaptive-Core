from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

from adaptive_core.v3.reason_ids import ReasonId

ADAMANTINE_ADVISORY_EVIDENCE_VERSION = "adaptive_core_oracle_v3"

_ALLOWED_ROOT_KEYS = {
    "ac_iface_version",
    "context_hash",
    "issued_at",
    "expires_at",
    "generated_at",
    "overall_score",
    "signals",
    "oracle_version",
    "external_source_id",
}

_FORBIDDEN_AUTHORITY_KEYS = {
    "allow",
    "approve",
    "approved",
    "authority",
    "authorization",
    "bypass",
    "final_approval",
    "grant_execution",
    "handoff_allowed",
    "override",
}


def _fail(message: str) -> "NoReturn":  # type: ignore[name-defined]
    raise ValueError(f"{ReasonId.AC_V3_REPORT_INVALID.value}: {message}")


def _contains_forbidden_authority_field(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if isinstance(key, str) and key in _FORBIDDEN_AUTHORITY_KEYS:
                return True
            if _contains_forbidden_authority_field(child):
                return True
    elif isinstance(value, list):
        return any(_contains_forbidden_authority_field(item) for item in value)
    return False


def _require_non_empty_str(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{field} must be a non-empty string")
    return value.strip()


def _require_int(value: Any, field: str) -> int:
    if not isinstance(value, int):
        _fail(f"{field} must be an integer")
    return value


def _validate_signals(signals: Any) -> list[dict[str, Any]]:
    if not isinstance(signals, Sequence) or isinstance(signals, (str, bytes)) or not signals:
        _fail("signals must be a non-empty sequence")

    normalized: list[dict[str, Any]] = []
    for index, signal in enumerate(signals):
        if not isinstance(signal, Mapping):
            _fail(f"signals[{index}] must be an object")
        source = _require_non_empty_str(signal.get("source"), f"signals[{index}].source")
        severity = _require_int(signal.get("severity"), f"signals[{index}].severity")
        if not 0 <= severity <= 100:
            _fail(f"signals[{index}].severity must be between 0 and 100")
        reason_ids = signal.get("reason_ids")
        if not isinstance(reason_ids, Sequence) or isinstance(reason_ids, (str, bytes)) or not reason_ids:
            _fail(f"signals[{index}].reason_ids must be a non-empty sequence")
        normalized_reason_ids = [
            _require_non_empty_str(reason_id, f"signals[{index}].reason_ids") for reason_id in reason_ids
        ]
        normalized.append({"source": source, "severity": severity, "reason_ids": normalized_reason_ids})
    return normalized


def build_adamantine_advisory_evidence_v1(
    *,
    context_hash: str,
    issued_at: int,
    expires_at: int,
    generated_at: int,
    overall_score: int,
    signals: Sequence[Mapping[str, Any]] | None = None,
    oracle_version: str = "adaptive-core/3.0.0",
    external_source_id: str = "adaptive-core-v3-adamantine-export",
) -> dict[str, Any]:
    """Build AdamantineOS-consumable Adaptive Core advisory evidence.

    The exported object intentionally matches AdamantineOS' existing
    ``adaptive_core_oracle_v3`` evidence boundary. It is advisory evidence only;
    it never carries final approval, override, bypass, or handoff authority.
    """

    payload: dict[str, Any] = {
        "ac_iface_version": ADAMANTINE_ADVISORY_EVIDENCE_VERSION,
        "context_hash": context_hash,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "generated_at": generated_at,
        "overall_score": overall_score,
        "signals": list(signals) if signals is not None else [
            {"source": "adaptive-core", "severity": 5, "reason_ids": ["ok"]}
        ],
        "oracle_version": oracle_version,
        "external_source_id": external_source_id,
    }
    return validate_adamantine_advisory_evidence_v1(payload)


def validate_adamantine_advisory_evidence_v1(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate an AdamantineOS-facing Adaptive Core advisory evidence object."""

    if not isinstance(payload, Mapping):
        _fail("payload must be an object")

    unknown = sorted(set(payload.keys()) - _ALLOWED_ROOT_KEYS)
    if unknown:
        _fail(f"unknown fields: {unknown}")

    if _contains_forbidden_authority_field(payload):
        _fail("authority fields are forbidden")

    if payload.get("ac_iface_version") != ADAMANTINE_ADVISORY_EVIDENCE_VERSION:
        _fail(f"ac_iface_version must be {ADAMANTINE_ADVISORY_EVIDENCE_VERSION}")

    context_hash = _require_non_empty_str(payload.get("context_hash"), "context_hash")
    issued_at = _require_int(payload.get("issued_at"), "issued_at")
    expires_at = _require_int(payload.get("expires_at"), "expires_at")
    generated_at = _require_int(payload.get("generated_at"), "generated_at")
    overall_score = _require_int(payload.get("overall_score"), "overall_score")

    if expires_at < issued_at:
        _fail("expires_at must be greater than or equal to issued_at")
    if generated_at <= 0:
        _fail("generated_at must be positive")
    if not 0 <= overall_score <= 100:
        _fail("overall_score must be between 0 and 100")

    oracle_version = payload.get("oracle_version")
    external_source_id = payload.get("external_source_id")
    if oracle_version is not None:
        oracle_version = _require_non_empty_str(oracle_version, "oracle_version")
    if external_source_id is not None:
        external_source_id = _require_non_empty_str(external_source_id, "external_source_id")

    return {
        "ac_iface_version": ADAMANTINE_ADVISORY_EVIDENCE_VERSION,
        "context_hash": context_hash,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "generated_at": generated_at,
        "overall_score": overall_score,
        "signals": _validate_signals(payload.get("signals")),
        "oracle_version": oracle_version,
        "external_source_id": external_source_id,
    }
