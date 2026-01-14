from __future__ import annotations

import pytest

from adaptive_core.threat_packet import ThreatPacket


def _base(**overrides):
    data = {
        "source_layer": "sentinel_ai_v2",
        "threat_type": "reorg",
        "severity": 5,
        "description": "x",
    }
    data.update(overrides)
    return data


def test_timestamp_autofill_and_parseable_when_provided():
    # auto-fill when missing/empty
    p1 = ThreatPacket(**_base(timestamp=""))
    assert isinstance(p1.timestamp, str)
    assert p1.timestamp.endswith("Z")

    # if provided, must be parseable
    p2 = ThreatPacket(**_base(timestamp="2026-01-14T00:00:00Z"))
    assert p2.timestamp == "2026-01-14T00:00:00Z"


def test_timestamp_rejects_invalid_format():
    with pytest.raises(ValueError) as e:
        ThreatPacket(**_base(timestamp="not-a-timestamp"))
    assert "Invalid timestamp format" in str(e.value)


def test_correlation_id_autofill_and_reject_blank_when_provided():
    # auto-generate when empty
    p1 = ThreatPacket(**_base(correlation_id=""))
    assert isinstance(p1.correlation_id, str)
    assert len(p1.correlation_id) > 10  # uuid-like

    # provided but whitespace-only => reject
    with pytest.raises(ValueError) as e:
        ThreatPacket(**_base(correlation_id="   "))
    assert "correlation_id" in str(e.value)


def test_severity_clamped_and_rejects_non_int_like():
    # clamp low
    p_low = ThreatPacket(**_base(severity=-99))
    assert p_low.severity == 0

    # clamp high
    p_high = ThreatPacket(**_base(severity=999))
    assert p_high.severity == 10

    # reject non-int-like
    with pytest.raises(ValueError) as e:
        ThreatPacket(**_base(severity="nope"))
    assert "severity must be an int-like value" in str(e.value)


def test_metadata_default_and_rejects_non_dict():
    p = ThreatPacket(**_base(metadata=None))
    assert isinstance(p.metadata, dict)

    with pytest.raises(ValueError) as e:
        ThreatPacket(**_base(metadata=["bad"]))  # type: ignore[arg-type]
    assert "metadata must be a dict" in str(e.value)


def test_from_dict_rejects_non_dict():
    with pytest.raises(ValueError) as e:
        ThreatPacket.from_dict("not-a-dict")  # type: ignore[arg-type]
    assert "expects a dict" in str(e.value)
