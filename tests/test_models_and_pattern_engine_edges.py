from __future__ import annotations

import pytest

from adaptive_core.models import ThreatPacket
from adaptive_core.pattern_engine import PatternEngine


# -------------------------
# models.py (lines 71–72)
# -------------------------

def test_threat_packet_from_mapping_rejects_invalid_evidence_type() -> None:
    with pytest.raises(ValueError):
        ThreatPacket.from_mapping(
            {
                "packet_id": "p1",
                "source_layer": "DQSN",
                "severity": 0.5,
                "evidence": "not-a-dict",  # invalid
                "meta": {},
            }
        )


def test_threat_packet_from_mapping_rejects_invalid_meta_type() -> None:
    with pytest.raises(ValueError):
        ThreatPacket.from_mapping(
            {
                "packet_id": "p2",
                "source_layer": "DQSN",
                "severity": 0.5,
                "evidence": {},
                "meta": "not-a-dict",  # invalid
            }
        )


# -------------------------
# pattern_engine.py (91,105)
# -------------------------

def test_pattern_engine_skips_non_positive_severity() -> None:
    engine = PatternEngine()

    pkt = ThreatPacket(
        packet_id="p1",
        source_layer="DQSN",
        severity=0.0,  # <= 0 triggers skip branch
        evidence={},
        meta={},
    )

    findings = engine.process_packets([pkt])
    assert findings == []


def test_pattern_engine_returns_empty_for_no_packets() -> None:
    engine = PatternEngine()

    findings = engine.process_packets([])
    assert findings == []
