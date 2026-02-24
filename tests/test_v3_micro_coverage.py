from __future__ import annotations

import json
from typing import Any, Dict

import pytest

from adaptive_core.v3.confidence import ConfidenceWeights, load_confidence_weights
from adaptive_core.v3.correlation import (
    CorrelationSnapshot,
    aggregate_node_summaries,
    generate_correlation_findings,
)
from adaptive_core.v3.events import ObservedEventV3
from adaptive_core.v3.graph import render_drift_dot
from adaptive_core.v3.findings import FindingV3
from adaptive_core.v3.node_summary import NodeSummaryEventV3


# -------------------------
# confidence.py (lines 23,27,34,38)
# -------------------------

def test_confidence_weights_validate_rejects_out_of_range() -> None:
    # Hits confidence.py line 23: "weight out of range"
    cw = ConfidenceWeights(
        version="v3",
        recurrence=1.2,  # out of range
        severity=0.0,
        reproducibility=0.0,
        cross_layer_impact=0.0,
    )
    with pytest.raises(ValueError) as e:
        cw.validate()
    assert "AC_V3_CONF_WEIGHTS_INVALID" in str(e.value)


def test_confidence_weights_validate_rejects_bad_sum() -> None:
    # Hits confidence.py line 27: "weights must sum to 1.0"
    cw = ConfidenceWeights(
        version="v3",
        recurrence=0.25,
        severity=0.25,
        reproducibility=0.25,
        cross_layer_impact=0.10,  # sum = 0.85
    )
    with pytest.raises(ValueError) as e:
        cw.validate()
    assert "AC_V3_CONF_WEIGHTS_INVALID" in str(e.value)
    assert "weights must sum to 1.0" in str(e.value)


def test_load_confidence_weights_rejects_invalid_root(monkeypatch: pytest.MonkeyPatch) -> None:
    # Hits confidence.py line 34: invalid root
    import adaptive_core.v3.confidence as conf

    class _Fake:
        def joinpath(self, *_: Any, **__: Any) -> "_Fake":
            return self

        def read_text(self, encoding: str = "utf-8") -> str:
            return json.dumps({"nope": True})

    monkeypatch.setattr(conf.resources, "files", lambda *_args, **_kwargs: _Fake())

    with pytest.raises(ValueError) as e:
        load_confidence_weights()
    assert "AC_V3_CONF_WEIGHTS_INVALID" in str(e.value)
    assert "invalid root" in str(e.value)


def test_load_confidence_weights_rejects_weights_not_object(monkeypatch: pytest.MonkeyPatch) -> None:
    # Hits confidence.py line 38: weights must be object
    import adaptive_core.v3.confidence as conf

    class _Fake:
        def joinpath(self, *_: Any, **__: Any) -> "_Fake":
            return self

        def read_text(self, encoding: str = "utf-8") -> str:
            return json.dumps({"version": "v3", "weights": "nope"})

    monkeypatch.setattr(conf.resources, "files", lambda *_args, **_kwargs: _Fake())

    with pytest.raises(ValueError) as e:
        load_confidence_weights()
    assert "AC_V3_CONF_WEIGHTS_INVALID" in str(e.value)
    assert "weights must be object" in str(e.value)


# -------------------------
# correlation.py (lines 37,62)
# -------------------------

def test_aggregate_node_summaries_skips_nonpositive_counts() -> None:
    # Hits correlation.py line 37: continue for count <= 0
    ev = NodeSummaryEventV3(
        node_id="n1",
        window_start="2026-02-24T00:00:00Z",
        window_end="2026-02-24T01:00:00Z",
        total_events=5,
        by_upstream_reason_id={"RID_OK": 3, "RID_ZERO": 0, "RID_NEG": -2},
    )
    snap = aggregate_node_summaries([ev])
    assert snap.by_upstream_reason_id == {"RID_OK": 3}
    assert snap.nodes_reporting_reason_id == {"RID_OK": 1}


def test_generate_correlation_findings_returns_empty_when_no_nodes() -> None:
    # Hits correlation.py line 62: total_nodes <= 0 => return []
    snap = CorrelationSnapshot(
        total_nodes=0,
        total_events=0,
        by_upstream_reason_id={},
        nodes_reporting_reason_id={},
    )
    out = generate_correlation_findings(snap)
    assert out == []


# -------------------------
# events.py (line 48)
# -------------------------

def test_observed_event_from_mapping_executes_constructor() -> None:
    # Hits events.py line 48: from_mapping() path
    ev = ObservedEventV3.from_mapping(
        {
            "source_layer": "DQSN",
            "event_type": "anomaly",
            "severity": 0.7,
            "timestamp": "2026-02-24T00:00:00Z",
            "correlation_id": "c1",
            "meta": {"k": "v"},
            "reason_id": "RID-1",
        }
    )
    assert ev.source_layer == "DQSN"
    assert ev.reason_id == "RID-1"
    assert ev.meta == {"k": "v"}


# -------------------------
# graph.py (line 23)
# -------------------------

def test_render_drift_dot_skips_non_drift_findings() -> None:
    # Hits graph.py line 23: continue when finding_id doesn't start with "AC-DRIFT::"
    good = FindingV3(
        finding_id="AC-DRIFT::ASSUMPTION-MISMATCH::X",
        title="t",
        severity=0.1,
        evidence={"assumption_key": "meta.canonical", "layers": ["DQSN"]},
        guardrails=["AMG-001"],
    )
    bad = FindingV3(
        finding_id="AC-CORR::REASON-WIDESPREAD::RID",
        title="t",
        severity=0.1,
        evidence={"assumption_key": "meta.canonical", "layers": ["QWG"]},
        guardrails=["AMG-001"],
    )

    dot = render_drift_dot([bad, good])
    # bad must be ignored; only DQSN edge appears
    assert '"DQSN" -> "meta.canonical";' in dot
    assert '"QWG" -> "meta.canonical";' not in dot
