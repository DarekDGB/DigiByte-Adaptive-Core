# tests/test_immune_report.py

from __future__ import annotations

from adaptive_core.engine import AdaptiveEngine
from adaptive_core.threat_memory import ThreatMemory
from adaptive_core.threat_packet import ThreatPacket
from pathlib import Path


def _packet(
    i: int,
    severity: int = 5,
    threat_type: str = "test_threat",
    source_layer: str = "sentinel",
) -> ThreatPacket:
    return ThreatPacket(
        source_layer=source_layer,
        threat_type=threat_type,
        severity=severity,
        description="immune-report-test",
        timestamp="2025-01-01T00:00:00Z",
        node_id=f"node-{i}",
        wallet_id=None,
        tx_id=None,
        block_height=i,
    )


def _engine_with_packets(tmp_path) -> AdaptiveEngine:
    mem_path: Path = tmp_path / "memory.json"
    store = ThreatMemory(path=mem_path, max_packets=500)
    engine = AdaptiveEngine()

    # Feed the engine via public API so ThreatMemory + metadata are used.
    for i in range(10):
        engine.receive_threat_packet(_packet(i))

    # Add some variety for patterns / correlations
    engine.receive_threat_packet(_packet(100, severity=8, threat_type="high_sev"))
    engine.receive_threat_packet(
        _packet(101, severity=9, threat_type="high_sev", source_layer="guardian")
    )

    return engine


def test_threat_insights_returns_text(tmp_path) -> None:
    engine = _engine_with_packets(tmp_path)

    text = engine.threat_insights(min_severity=0)

    assert isinstance(text, str)
    assert "Test Threat" in text or "High Sev" in text


def test_generate_immune_report_structure(tmp_path) -> None:
    engine = _engine_with_packets(tmp_path)

    report = engine.generate_immune_report(
        min_severity=0,
        pattern_window=5,
        trend_bucket="hour",
        last_n=3,
    )

    # Top-level keys
    for key in ["summary", "analysis", "patterns", "correlations", "trends", "text"]:
        assert key in report

    # Summary and analysis should be consistent
    assert isinstance(report["summary"], dict)
    assert isinstance(report["analysis"], dict)
    assert isinstance(report["text"], str)
    assert report["analysis"]["total_count"] >= len(report["summary"])

    # Patterns structure
    patterns = report["patterns"]
    assert "window_size" in patterns
    assert "total_considered" in patterns
    assert "rising_patterns" in patterns
    assert "hotspot_layers" in patterns

    # Correlations structure
    correlations = report["correlations"]
    assert "pair_correlations" in correlations
    assert "layer_threat_combos" in correlations

    # Trends structure
    trends = report["trends"]
    assert "bucket" in trends
    assert "points" in trends
    assert "trend_direction" in trends
    assert "start_total" in trends
    assert "end_total" in trends
