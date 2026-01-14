from __future__ import annotations

from datetime import datetime
from dataclasses import fields, is_dataclass

from adaptive_core.memory import InMemoryAdaptiveStore
from adaptive_core.models import RiskEvent, AdaptiveState, FeedbackType


def _make_risk_event(**overrides):
    """
    Create a RiskEvent using deterministic placeholders + required known fields.
    Fail-closed: if schema changes, tests should surface it.
    """
    if not is_dataclass(RiskEvent):
        raise RuntimeError("RiskEvent must be a dataclass")

    # Required fields discovered from failures
    base = {
        "event_id": "evt-1",
        "risk_score": 0.7,
        "risk_level": "HIGH",
        "layer": "sentinel",
        "fingerprint": "fp-x",
        "feedback": list(FeedbackType)[0],
    }
    base.update(overrides)

    # Ensure we pass only known fields
    allowed = {f.name for f in fields(RiskEvent)}
    ctor = {k: v for k, v in base.items() if k in allowed}

    return RiskEvent(**ctor)


def test_store_events_filters_and_recent_events():
    store = InMemoryAdaptiveStore()

    e1 = _make_risk_event(event_id="evt-1", layer="sentinel", fingerprint="fp-a")
    e2 = _make_risk_event(event_id="evt-2", layer="dqsn", fingerprint="fp-b")
    e3 = _make_risk_event(event_id="evt-3", layer="sentinel", fingerprint="fp-b")

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

    store.add_event(_make_risk_event(event_id="evt-10", layer="sentinel", feedback=fb0))
    store.add_event(_make_risk_event(event_id="evt-11", layer="sentinel", feedback=fb0))
    store.add_event(_make_risk_event(event_id="evt-12", layer="dqsn", feedback=fb1))

    fstats = store.feedback_stats()
    assert fstats[fb0] == 2
    assert fstats[fb1] == 1

    lstats = store.layer_stats()
    assert lstats["sentinel"] == 2
    assert lstats["dqsn"] == 1


def test_store_snapshots_latest_none_and_copy_behavior():
    store = InMemoryAdaptiveStore()

    assert store.latest_snapshot() is None
    assert store.list_snapshots() == []

    state = AdaptiveState()
    store.save_snapshot(state)

    snap = store.latest_snapshot()
    assert snap is not None
    assert isinstance(snap.timestamp, datetime)

    # Snapshot must not be the same object
    assert snap.state is not state

    snaps = store.list_snapshots()
    assert len(snaps) == 1
    assert snaps[0] == snap
