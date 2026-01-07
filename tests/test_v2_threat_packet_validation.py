from __future__ import annotations

import pytest

from adaptive_core.threat_packet import ThreatPacket


def test_threat_packet_rejects_invalid_timestamp_when_provided():
    with pytest.raises(ValueError):
        ThreatPacket(
            source_layer="sentinel_ai_v2",
            threat_type="TEST",
            severity=5,
            description="bad timestamp",
            timestamp="not-a-timestamp",
        )


def test_threat_packet_autofills_timestamp_and_correlation_id_when_missing():
    p = ThreatPacket(
        source_layer="sentinel_ai_v2",
        threat_type="TEST",
        severity=5,
        description="auto fields",
        timestamp="",
        correlation_id="",
    )
    assert isinstance(p.timestamp, str) and len(p.timestamp) > 0
    assert isinstance(p.correlation_id, str) and len(p.correlation_id) > 0


def test_threat_packet_rejects_non_dict_metadata():
    with pytest.raises(ValueError):
        ThreatPacket(
            source_layer="sentinel_ai_v2",
            threat_type="TEST",
            severity=5,
            description="bad metadata",
            metadata=["not", "a", "dict"],  # type: ignore[list-item]
        )
