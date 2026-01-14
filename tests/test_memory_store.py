from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import datetime

import pytest

from adaptive_core.memory import InMemoryAdaptiveStore
from adaptive_core.models import RiskEvent, AdaptiveState, FeedbackType


def _make_risk_event(**overrides):
    """
    Create a RiskEvent without guessing its full constructor.
    We fill required fields deterministically with safe placeholders.
    """
    if not is_dataclass(RiskEvent):
        raise RuntimeError("RiskEvent must be a dataclass for this test helper")

    values = {}
    for f in fields(RiskEvent):
        # Use explicit override if provided
        if f.name in overrides:
            values[f.name] = overrides[f.name]
            continue

        # Provide deterministic defaults by type/name
        if f.type is str:
            values[f.name] = f"{f.name}-x"
        elif f.type is int:
            values[f.name] = 1
        elif f.type is float:
            values[f.name] = 0.1
        elif f.type is bool:
            values[f.name] = False
        elif f.type is datetime:
            values[f.name] = datetime(2026, 1, 14, 0, 0, 0)
        else:
            # Known enums used in your store:
            if f.name == "feedback":
                values[f.name] = list(FeedbackType)[0]
            else:
                # If the dataclass has a default/default_factory, we can omit it
                if f.default is not f.default_factory:  # type: ignore[attr-defined]
                    # keep as-is; dataclasses will use defaults if we omit
                    pass

    # Remove keys we couldn't fill and that may have defaults
    # (dataclasses will use default/default_factory if not present)
    ctor_kwargs = {}
    for f in fields(RiskEvent):
        if f.name in values:
            ctor_kwargs[f.name] = values[f.name]

    return RiskEvent(**ctor_kwargs)


def test_store_events_filters_and_recent_events():
    store = InMemoryAdaptiveStore()

    e1 = _make_risk_event(layer="sentinel", fingerprint="fp-a")
    e2 = _make_risk_event(layer="dqsn", fingerprint="fp-b")
    e3 = _make_risk_event(layer="sentinel", fingerprint="fp-b")

    store.add_event(e1)
    store.add_event(e2)
    store.add_event(e3)

    assert store.list_events() == [e1, e2, e3]

    # recent_events: last N
    assert list(store.recent_events(limit=2)) == [e2, e3]
    # limit larger than size should just return all
    assert list(store.recent_events(limit=99)) == [e1, e2, e3]

    # filters
    assert store.events_by_layer("sentinel") == [e1, e3]
    assert store.events_by_layer("missing") == []
    assert store.events_by_fingerprint("fp-b") == [e2, e3]
    assert store.events_by_fingerprint("none") == []


def test_store_stats_helpers():
    store = InMemoryAdaptiveStore()

    fb0 = list(FeedbackType)[0]
    fb1 = list(FeedbackType)[-1]

    store.add_event(_make_risk_event(layer="sentinel", feedback=fb0))
    store.add_event(_make_risk_event(layer="sentinel", feedback=fb0))
    store.add_event(_make_risk_event(layer="dqsn", feedback=fb1))

    fstats = store.feedback_stats()
    assert fstats[fb0] == 2
    assert fstats[fb1] == 1

    lstats = store.layer_stats()
    assert lstats["sentinel"] == 2
    assert lstats["dqsn"] == 1


def test_store_snapshots_latest_none_and_copy_behavior():
    store = InMemoryAdaptiveStore()

    # latest_snapshot on empty store
    assert store.latest_snapshot() is None
    assert store.list_snapshots() == []

    # save snapshot and ensure it's stored
    state = AdaptiveState()
    store.save_snapshot(state)
    snap = store.latest_snapshot()
    assert snap is not None
    assert snap.state is not state  # must be a copy, not same object

    # list_snapshots returns list form
    snaps = store.list_snapshots()
    assert len(snaps) == 1
    assert snaps[0] == snap
