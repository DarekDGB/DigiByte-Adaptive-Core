from __future__ import annotations

import pytest

from adaptive_core.v3.canonicalize import canonicalize_event


def _base(**overrides):
    raw = {
        "source_layer": "sentinel_ai_v3",
        "event_type": "block_stall",
        "severity": 0.5,
        "timestamp": "2026-01-14T00:00:00Z",
        "correlation_id": "cid-1",
        "meta": {"k": "v"},
        "reason_id": None,
    }
    raw.update(overrides)
    return raw


def test_canonicalize_happy_path_returns_result_and_hash():
    res = canonicalize_event(_base())
    assert res.event.source_layer == "sentinel_ai_v3"
    assert res.event.event_type == "block_stall"
    assert abs(res.event.severity - 0.5) < 1e-12
    assert res.event.timestamp.endswith("Z")
    assert res.event.correlation_id == "cid-1"
    assert res.event.meta == {"k": "v"}
    assert res.event.reason_id is None
    assert isinstance(res.context_hash, str)
    assert len(res.context_hash) > 10


def test_raw_must_be_mapping():
    with pytest.raises(ValueError) as e:
        canonicalize_event(["not", "a", "mapping"])  # type: ignore[arg-type]
    assert "AC_V3_INVALID_EVENT" in str(e.value)


def test_missing_required_field():
    d = _base()
    del d["event_type"]
    with pytest.raises(ValueError) as e:
        canonicalize_event(d)
    assert "AC_V3_MISSING_FIELD" in str(e.value)


def test_require_str_rejects_empty_or_non_str():
    with pytest.raises(ValueError) as e:
        canonicalize_event(_base(source_layer="   "))
    assert "AC_V3_TYPE_INVALID" in str(e.value)

    with pytest.raises(ValueError) as e2:
        canonicalize_event(_base(correlation_id=123))  # type: ignore[arg-type]
    assert "AC_V3_TYPE_INVALID" in str(e2.value)


def test_severity_must_be_float_and_in_0_1():
    with pytest.raises(ValueError) as e:
        canonicalize_event(_base(severity="nope"))  # type: ignore[arg-type]
    assert "AC_V3_TYPE_INVALID" in str(e.value)

    with pytest.raises(ValueError) as e2:
        canonicalize_event(_base(severity=-0.1))
    assert "AC_V3_NON_CANONICAL" in str(e2.value)

    with pytest.raises(ValueError) as e3:
        canonicalize_event(_base(severity=1.1))
    assert "AC_V3_NON_CANONICAL" in str(e3.value)


def test_timestamp_requires_Z_and_parseable_iso():
    with pytest.raises(ValueError) as e:
        canonicalize_event(_base(timestamp="2026-01-14T00:00:00"))  # missing Z
    assert "AC_V3_TIMESTAMP_INVALID" in str(e.value)

    with pytest.raises(ValueError) as e2:
        canonicalize_event(_base(timestamp="not-a-timeZ"))
    assert "AC_V3_TIMESTAMP_INVALID" in str(e2.value)


def test_meta_must_be_dict_and_keys_must_be_str():
    with pytest.raises(ValueError) as e:
        canonicalize_event(_base(meta=["bad"]))  # type: ignore[arg-type]
    assert "AC_V3_META_INVALID" in str(e.value)

    with pytest.raises(ValueError) as e2:
        canonicalize_event(_base(meta={1: "x"}))  # type: ignore[arg-type]
    assert "AC_V3_META_INVALID" in str(e2.value)


def test_reason_id_optional_but_if_present_must_be_non_empty_str():
    # ok: non-empty str
    res = canonicalize_event(_base(reason_id="RSN-1"))
    assert res.event.reason_id == "RSN-1"

    # bad: empty/whitespace
    with pytest.raises(ValueError) as e:
        canonicalize_event(_base(reason_id="   "))
    assert "AC_V3_TYPE_INVALID" in str(e.value)

    # bad: non-str
    with pytest.raises(ValueError) as e2:
        canonicalize_event(_base(reason_id=123))  # type: ignore[arg-type]
    assert "AC_V3_TYPE_INVALID" in str(e2.value)

def test_missing_severity_field_raises_missing_field():
    d = _base()
    del d["severity"]
    with pytest.raises(ValueError) as e:
        canonicalize_event(d)
    assert "AC_V3_MISSING_FIELD" in str(e.value)
