from __future__ import annotations

from adaptive_core.engine import AdaptiveEngine
from adaptive_core.threat_packet import ThreatPacket


def test_analysis_is_deterministic_for_same_inputs():
    engine = AdaptiveEngine()

    packets = [
        ThreatPacket(
            source_layer="sentinel_ai_v2",
            threat_type="REORG",
            severity=7,
            description="chain reorg",
            timestamp="2026-01-01T10:00:00Z",
        ),
        ThreatPacket(
            source_layer="adn_v2",
            threat_type="WALLET_ANOMALY",
            severity=5,
            description="wallet anomaly",
            timestamp="2026-01-01T11:00:00Z",
        ),
        ThreatPacket(
            source_layer="dqsn_v2",
            threat_type="NETWORK_SPIKE",
            severity=6,
            description="network spike",
            timestamp="2026-01-01T12:00:00Z",
        ),
    ]

    for p in packets:
        engine.receive_threat_packet(p)

    analysis_1 = engine.analyze_threats(min_severity=0)
    analysis_2 = engine.analyze_threats(min_severity=0)

    assert analysis_1 == analysis_2
