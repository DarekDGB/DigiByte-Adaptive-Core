from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from typing import Dict

from .reason_ids import ReasonId


@dataclass(frozen=True, slots=True)
class ConfidenceWeights:
    version: str
    recurrence: float
    severity: float
    reproducibility: float
    cross_layer_impact: float

    def validate(self) -> None:
        vals = [self.recurrence, self.severity, self.reproducibility, self.cross_layer_impact]
        for v in vals:
            if not isinstance(v, float) or v < 0.0 or v > 1.0:
                raise ValueError(f"{ReasonId.AC_V3_CONF_WEIGHTS_INVALID.value}: weight out of range")
        s = sum(vals)
        # strict deterministic tolerance
        if abs(s - 1.0) > 1e-9:
            raise ValueError(f"{ReasonId.AC_V3_CONF_WEIGHTS_INVALID.value}: weights must sum to 1.0, got {s}")


def load_confidence_weights() -> ConfidenceWeights:
    text = resources.files("adaptive_core.v3").joinpath("confidence_weights_v3.json").read_text(encoding="utf-8")
    data = json.loads(text)
    if not isinstance(data, dict) or "version" not in data or "weights" not in data:
        raise ValueError(f"{ReasonId.AC_V3_CONF_WEIGHTS_INVALID.value}: invalid root")

    w = data["weights"]
    if not isinstance(w, dict):
        raise ValueError(f"{ReasonId.AC_V3_CONF_WEIGHTS_INVALID.value}: weights must be object")

    cw = ConfidenceWeights(
        version=str(data["version"]),
        recurrence=float(w.get("recurrence", -1.0)),
        severity=float(w.get("severity", -1.0)),
        reproducibility=float(w.get("reproducibility", -1.0)),
        cross_layer_impact=float(w.get("cross_layer_impact", -1.0)),
    )
    cw.validate()
    return cw


def compute_confidence(
    *,
    recurrence_ratio: float,
    avg_severity: float,
    reproducibility: float,
    cross_layer_impact: float,
    weights: ConfidenceWeights,
) -> float:
    """
    Deterministic confidence score in [0.0, 1.0].
    Inputs must already be bounded.
    """
    def clamp(x: float) -> float:
        return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x

    r = clamp(recurrence_ratio)
    s = clamp(avg_severity)
    rp = clamp(reproducibility)
    cli = clamp(cross_layer_impact)

    score = (
        weights.recurrence * r
        + weights.severity * s
        + weights.reproducibility * rp
        + weights.cross_layer_impact * cli
    )
    return clamp(score)
