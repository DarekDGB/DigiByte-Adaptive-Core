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


def test_node_summary_all_error_branches_smoke():
    # 1) raw must be mapping
    with pytest.raises(ValueError):
        canonicalize_node_summary(["nope"])  # type: ignore[arg-type]

    # 2) node_id missing
    d = _base()
    del d["node_id"]
    with pytest.raises(ValueError):
        canonicalize_node_summary(d)

    # 3) node_id invalid type
    with pytest.raises(ValueError):
        canonicalize_node_summary(_base(node_id=None))  # type: ignore[arg-type]

    # 4) window_start missing Z
    with pytest.raises(ValueError):
        canonicalize_node_summary(_base(window_start="2026-01-14T00:00:00"))

    # 5) window_end invalid iso
    with pytest.raises(ValueError):
        canonicalize_node_summary(_base(window_end="not-a-timeZ"))

    # 6) total_events missing
    d2 = _base()
    del d2["total_events"]
    with pytest.raises(ValueError):
        canonicalize_node_summary(d2)

    # 7) total_events bool rejected (explicit branch)
    with pytest.raises(ValueError):
        canonicalize_node_summary(_base(total_events=True))  # type: ignore[arg-type]

    # 8) total_events non-int
    with pytest.raises(ValueError):
        canonicalize_node_summary(_base(total_events="nope"))  # type: ignore[arg-type]

    # 9) total_events negative
    with pytest.raises(ValueError):
        canonicalize_node_summary(_base(total_events=-1))

    # 10) by_upstream_reason_id missing
    d3 = _base()
    del d3["by_upstream_reason_id"]
    with pytest.raises(ValueError):
        canonicalize_node_summary(d3)

    # 11) by_upstream_reason_id not dict
    with pytest.raises(ValueError):
        canonicalize_node_summary(_base(by_upstream_reason_id=["bad"]))  # type: ignore[arg-type]

    # 12) by_upstream_reason_id key invalid (empty)
    with pytest.raises(ValueError):
        canonicalize_node_summary(_base(by_upstream_reason_id={"": 1}))

    # 13) by_upstream_reason_id key invalid (non-string)
    with pytest.raises(ValueError):
        canonicalize_node_summary(_base(by_upstream_reason_id={1: 2}))  # type: ignore[dict-item]

    # 14) by_upstream_reason_id value invalid (bool)
    with pytest.raises(ValueError):
        canonicalize_node_summary(_base(by_upstream_reason_id={"X": False}))  # type: ignore[arg-type]

    # 15) by_upstream_reason_id value invalid (non-int)
    with pytest.raises(ValueError):
        canonicalize_node_summary(_base(by_upstream_reason_id={"X": "nope"}))  # type: ignore[arg-type]

    # 16) by_upstream_reason_id value invalid (negative)
    with pytest.raises(ValueError):
        canonicalize_node_summary(_base(by_upstream_reason_id={"X": -1}))
