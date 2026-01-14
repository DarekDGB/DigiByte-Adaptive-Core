from __future__ import annotations

import pytest

from adaptive_core.v3.node_summary import canonicalize_node_summary


def _base(**overrides):
    raw = {
        "node_id": "node-1",
        "window_start": "2026-01-14T00:00:00Z",
        "window_end": "2026-01-14T01:00:00Z",
        "total_events": 3,
        "by_upstream_reason_id": {"X": 1, "Y": 2},
    }
    raw.update(overrides)
    return raw


def test_canonicalize_happy_path_returns_event_and_context_hash():
    ev, ctx = canonicalize_node_summary(_base())
    assert ev.node_id == "node-1"
    assert ev.total_events == 3
    assert ev.by_upstream_reason_id == {"X": 1, "Y": 2}
    assert isinstance(ctx, str)
    assert len(ctx) > 10


def test_raw_must_be_mapping():
    with pytest.raises(ValueError) as e:
        canonicalize_node_summary(["not", "a", "mapping"])  # type: ignore[arg-type]
    assert "AC_V3_INVALID_EVENT" in str(e.value)


def test_missing_required_field():
    with pytest.raises(ValueError) as e:
        canonicalize_node_summary(_base(node_id=None))  # type: ignore[arg-type]
    # type invalid for node_id
    assert "AC_V3_TYPE_INVALID" in str(e.value)

    with pytest.raises(ValueError) as e2:
        d = _base()
        del d["node_id"]
        canonicalize_node_summary(d)
    assert "AC_V3_MISSING_FIELD" in str(e2.value)


def test_iso_fields_require_Z_and_parseable():
    with pytest.raises(ValueError) as e:
        canonicalize_node_summary(_base(window_start="2026-01-14T00:00:00"))
    assert "AC_V3_TIMESTAMP_INVALID" in str(e.value)

    with pytest.raises(ValueError) as e2:
        canonicalize_node_summary(_base(window_end="not-a-timeZ"))
    assert "AC_V3_TIMESTAMP_INVALID" in str(e2.value)


def test_total_events_must_be_int_ge0_and_not_bool():
    with pytest.raises(ValueError) as e:
        canonicalize_node_summary(_base(total_events=True))  # bool rejected
    assert "AC_V3_TYPE_INVALID" in str(e.value)

    with pytest.raises(ValueError) as e2:
        canonicalize_node_summary(_base(total_events="nope"))
    assert "AC_V3_TYPE_INVALID" in str(e2.value)

    with pytest.raises(ValueError) as e3:
        canonicalize_node_summary(_base(total_events=-1))
    assert "AC_V3_NON_CANONICAL" in str(e3.value)


def test_by_upstream_reason_id_must_be_dict_and_valid_counts():
    with pytest.raises(ValueError) as e:
        canonicalize_node_summary(_base(by_upstream_reason_id=["bad"]))  # type: ignore[arg-type]
    assert "AC_V3_TYPE_INVALID" in str(e.value)

    with pytest.raises(ValueError) as e2:
        canonicalize_node_summary(_base(by_upstream_reason_id={"": 1}))
    assert "AC_V3_TYPE_INVALID" in str(e2.value)

    with pytest.raises(ValueError) as e3:
        canonicalize_node_summary(_base(by_upstream_reason_id={"X": True}))
    assert "AC_V3_TYPE_INVALID" in str(e3.value)

    with pytest.raises(ValueError) as e4:
        canonicalize_node_summary(_base(by_upstream_reason_id={"X": "nope"}))
    assert "AC_V3_TYPE_INVALID" in str(e4.value)

    with pytest.raises(ValueError) as e5:
        canonicalize_node_summary(_base(by_upstream_reason_id={"X": -1}))
    assert "AC_V3_NON_CANONICAL" in str(e5.value)


def test_missing_by_upstream_reason_id():
    d = _base()
    del d["by_upstream_reason_id"]
    with pytest.raises(ValueError) as e:
        canonicalize_node_summary(d)
    assert "AC_V3_MISSING_FIELD" in str(e.value)

def test_node_summary_window_start_missing_Z_hits_timestamp_invalid():
    with pytest.raises(ValueError) as e:
        canonicalize_node_summary(_base(window_start="2026-01-14T00:00:00"))  # no Z
    assert "AC_V3_TIMESTAMP_INVALID" in str(e.value)

def test_node_summary_window_end_invalid_iso_hits_parse_error_branch():
    # endswith Z so it passes the "must end with Z" check,
    # but invalid ISO so datetime.fromisoformat(...) throws.
    with pytest.raises(ValueError) as e:
        canonicalize_node_summary(_base(window_end="2026-13-99T99:99:99Z"))
    assert "AC_V3_TIMESTAMP_INVALID" in str(e.value)

def test_node_summary_window_start_invalid_iso_parse_branch():
    # Ends with Z, so it passes the "must end with Z" check,
    # then fails datetime.fromisoformat(...) to hit the parse error path.
    with pytest.raises(ValueError) as e:
        canonicalize_node_summary(_base(window_start="2026-13-99T99:99:99Z"))
    assert "AC_V3_TIMESTAMP_INVALID" in str(e.value)
