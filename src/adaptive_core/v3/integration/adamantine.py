from __future__ import annotations

import re

from typing import Any, Dict, Mapping, Sequence

from adaptive_core.v3.reason_ids import ReasonId

ADAMANTINE_ADVISORY_EVIDENCE_VERSION = "adaptive_core_oracle_v3"
_CONTEXT_HASH_RE = re.compile(r"^[0-9a-f]{64}$")

_ALLOWED_ROOT_KEYS = frozenset({
    "ac_iface_version",
    "context_hash",
    "issued_at",
    "expires_at",
    "generated_at",
    "overall_score",
    "signals",
    "oracle_version",
    "external_source_id",
})

_ALLOWED_SIGNAL_KEYS = frozenset({"source", "severity", "reason_ids"})


def _fail(message: str) -> "NoReturn":  # type: ignore[name-defined]
    raise ValueError(f"{ReasonId.AC_V3_REPORT_INVALID.value}: {message}")


def _unknown_field_names(value: Mapping[Any, Any], allowed: frozenset[str]) -> list[str]:
    unknown: set[str] = set()
    for key in value.keys():
        if type(key) is not str:
            unknown.add(f"<non-string:{type(key).__name__}>")
        elif key not in allowed:
            unknown.add(key)
    return sorted(unknown)


def _require_non_empty_str(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{field} must be a non-empty string")
    return value.strip()


def _require_context_hash(value: Any, field: str) -> str:
    text = _require_non_empty_str(value, field)
    if _CONTEXT_HASH_RE.fullmatch(text) is None:
        _fail(f"{field} must be lowercase 64-character hex")
    return text


def _require_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        _fail(f"{field} must be an integer")
    return value


def _validate_signals(signals: Any) -> list[dict[str, Any]]:
    if not isinstance(signals, Sequence) or isinstance(signals, (str, bytes)) or not signals:
        _fail("signals must be a non-empty sequence")

    normalized: list[dict[str, Any]] = []
    for index, signal in enumerate(signals):
        if not isinstance(signal, Mapping):
            _fail(f"signals[{index}] must be an object")
        unknown = _unknown_field_names(signal, _ALLOWED_SIGNAL_KEYS)
        if unknown:
            _fail(f"signals[{index}] unknown fields: {unknown}")
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
    now: int | None = None,
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
    return validate_adamantine_advisory_evidence_v1(payload, now=now)


def validate_adamantine_advisory_evidence_v1(payload: Mapping[str, Any], *, now: int | None = None) -> dict[str, Any]:
    """Validate an AdamantineOS-facing Adaptive Core advisory evidence object."""

    if not isinstance(payload, Mapping):
        _fail("payload must be an object")

    unknown = _unknown_field_names(payload, _ALLOWED_ROOT_KEYS)
    if unknown:
        _fail(f"unknown fields: {unknown}")

    if payload.get("ac_iface_version") != ADAMANTINE_ADVISORY_EVIDENCE_VERSION:
        _fail(f"ac_iface_version must be {ADAMANTINE_ADVISORY_EVIDENCE_VERSION}")

    context_hash = _require_context_hash(payload.get("context_hash"), "context_hash")
    issued_at = _require_int(payload.get("issued_at"), "issued_at")
    expires_at = _require_int(payload.get("expires_at"), "expires_at")
    generated_at = _require_int(payload.get("generated_at"), "generated_at")
    overall_score = _require_int(payload.get("overall_score"), "overall_score")

    if expires_at < issued_at:
        _fail("expires_at must be greater than or equal to issued_at")
    if now is not None:
        now = _require_int(now, "now")
        if issued_at > now:
            _fail("issued_at cannot be in the future")
        if expires_at < now:
            _fail("expires_at cannot be in the past")
    if generated_at <= 0:
        _fail("generated_at must be positive")
    if now is not None and generated_at > now:
        _fail("generated_at cannot be in the future")
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
