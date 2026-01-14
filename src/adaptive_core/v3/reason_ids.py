# src/adaptive_core/v3/reason_ids.py

from __future__ import annotations

from enum import Enum


class ReasonId(str, Enum):
    """
    Adaptive Core v3 reason IDs.

    Guardrail intent:
    - single source of truth (no magic strings)
    - stable, deterministic identifiers
    - fail-closed semantics
    """

    # Generic v3 ingestion/canonicalization failures
    AC_V3_INVALID_EVENT = "AC_V3_INVALID_EVENT"
    AC_V3_MISSING_FIELD = "AC_V3_MISSING_FIELD"
    AC_V3_TYPE_INVALID = "AC_V3_TYPE_INVALID"
    AC_V3_TIMESTAMP_INVALID = "AC_V3_TIMESTAMP_INVALID"
    AC_V3_META_INVALID = "AC_V3_META_INVALID"
    AC_V3_NON_CANONICAL = "AC_V3_NON_CANONICAL"

    # Guardrails / reporting / config failures
    AC_V3_GUARDRAIL_UNKNOWN = "AC_V3_GUARDRAIL_UNKNOWN"
    AC_V3_GUARDRAIL_REGISTRY_INVALID = "AC_V3_GUARDRAIL_REGISTRY_INVALID"
    AC_V3_CONF_WEIGHTS_INVALID = "AC_V3_CONF_WEIGHTS_INVALID"
    AC_V3_REPORT_INVALID = "AC_V3_REPORT_INVALID"
