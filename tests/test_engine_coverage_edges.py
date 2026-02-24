from __future__ import annotations

from adaptive_core.engine import AdaptiveEngine
from adaptive_core.models import RiskEvent
from adaptive_core.threat_packet import ThreatPacket


def _pkt(
    *,
    layer: str = "DQSN",
    ttype: str = "wallet_anomaly",
    sev: int = 5,
    ts: str = "2026-02-24T00:00:00Z",
) -> ThreatPacket:
    return ThreatPacket(
        source_layer=layer,
        threat_type=ttype,
        severity=sev,
        description="x",
        timestamp=ts,
        correlation_id="cid-1",
    )


def test_summarize_threats_filters_min_severity() -> None:
    e = AdaptiveEngine()
    e.receive_threat_packet(_pkt(sev=1, ttype="low"))
    e.receive_threat_packet(_pkt(sev=7, ttype="high"))

    out = e.summarize_threats(min_severity=5)
    assert out == {"high": 1}


def test_analyze_threats_empty_branch() -> None:
    e = AdaptiveEngine()
    e.receive_threat_packet(_pkt(sev=1))

    out = e.analyze_threats(min_severity=99)
    assert out["total_count"] == 0
    assert out["last_threats"] == []


def test_detect_threat_patterns_empty_branch() -> None:
    e = AdaptiveEngine()
    e.receive_threat_packet(_pkt(sev=1))

    out = e.detect_threat_patterns(min_severity=99, window=10)
    assert out["total_considered"] == 0
    assert out["rising_patterns"] == []
    assert out["hotspot_layers"] == []


def test_detect_threat_correlations_len_lt_2_branch() -> None:
    e = AdaptiveEngine()
    e.receive_threat_packet(_pkt(sev=5))

    out = e.detect_threat_correlations()
    assert out["pair_correlations"] == []
    assert out["layer_threat_combos"] == []


def test_detect_threat_trends_no_packets_branch() -> None:
    e = AdaptiveEngine()
    out = e.detect_threat_trends(min_severity=99, bucket="hour")
    assert out["trend_direction"] == "unknown"
    assert out["points"] == []
    assert out["invalid_timestamp_count"] == 0


def test_detect_threat_trends_all_invalid_timestamps_branch() -> None:
    e = AdaptiveEngine()
    p1 = _pkt(ts="2026-02-24T00:00:00Z")
    p2 = _pkt(ts="2026-02-24T01:00:00Z")

    # Mutate timestamps AFTER creation to bypass ThreatPacket validation
    p1.timestamp = "NOT-A-TIMESTAMP"
    p2.timestamp = "ALSO-BAD"

    e.receive_threat_packet(p1)
    e.receive_threat_packet(p2)

    out = e.detect_threat_trends(bucket="hour")
    assert out["points"] == []
    assert out["trend_direction"] == "unknown"
    assert out["invalid_timestamp_count"] == 2


def test_detect_threat_trends_increasing_branch() -> None:
    e = AdaptiveEngine()
    # start_total=1 (hour 00), end_total=2 (hour 01)
    e.receive_threat_packet(_pkt(ts="2026-02-24T00:10:00Z"))
    e.receive_threat_packet(_pkt(ts="2026-02-24T01:10:00Z"))
    e.receive_threat_packet(_pkt(ts="2026-02-24T01:20:00Z"))

    out = e.detect_threat_trends(bucket="hour")
    assert out["trend_direction"] == "increasing"


def test_detect_threat_trends_decreasing_branch() -> None:
    e = AdaptiveEngine()
    # start_total=2 (hour 00), end_total=1 (hour 01)
    e.receive_threat_packet(_pkt(ts="2026-02-24T00:10:00Z"))
    e.receive_threat_packet(_pkt(ts="2026-02-24T00:20:00Z"))
    e.receive_threat_packet(_pkt(ts="2026-02-24T01:10:00Z"))

    out = e.detect_threat_trends(bucket="hour")
    assert out["trend_direction"] == "decreasing"


def test_detect_threat_trends_flat_branch() -> None:
    e = AdaptiveEngine()
    # start_total=2 (hour 00), end_total=2 (hour 01)
    e.receive_threat_packet(_pkt(ts="2026-02-24T00:10:00Z"))
    e.receive_threat_packet(_pkt(ts="2026-02-24T00:20:00Z"))
    e.receive_threat_packet(_pkt(ts="2026-02-24T01:10:00Z"))
    e.receive_threat_packet(_pkt(ts="2026-02-24T01:20:00Z"))

    out = e.detect_threat_trends(bucket="hour")
    assert out["trend_direction"] == "flat"


def test_generate_immune_report_empty_sections_text_branches() -> None:
    e = AdaptiveEngine()

    r = e.generate_immune_report(min_severity=0)
    text = r["text"]

    # These asserts hit the exact "empty" text branches:
    assert "No threats recorded yet." in text
    assert "None detected." in text  # hotspot + rising patterns
    assert "No adjacent threat-type correlations detected." in text
    assert "No strong (layer, threat) combinations." in text


def test_threat_insights_empty_branch() -> None:
    e = AdaptiveEngine()
    assert e.threat_insights() == "No threats recorded yet."


def test_get_last_update_metadata_branch() -> None:
    e = AdaptiveEngine()
    meta = e.get_last_update_metadata()
    assert "last_threat_received" in meta
    assert "last_learning_update" in meta


def test_apply_learning_new_layer_and_string_feedback_tag_branch() -> None:
    e = AdaptiveEngine()

    ev = RiskEvent(
        event_id="e1",
        layer="NEW_LAYER",
        risk_score=0.9,
        risk_level="high",
    )
    # Force non-enum feedback to hit tag = str(fb).upper()
    ev.feedback = "true_positive"  # type: ignore[assignment]

    res = e.apply_learning([ev])

    # New layer created + adjustment object created
    assert "NEW_LAYER" in res.per_layer
    assert "NEW_LAYER" in res.state.layer_weights
