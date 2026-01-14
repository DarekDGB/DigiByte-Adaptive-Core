from __future__ import annotations

from typing import Any, Dict, Iterable, List

from adaptive_core.interface import AdaptiveCoreInterface
from adaptive_core.models import AdaptiveState


class _FakeEngine:
    def __init__(self) -> None:
        self.received_packets: List[Any] = []
        self.learn_calls: List[Any] = []
        self.state = AdaptiveState()

    def receive_threat_packet(self, packet: Any) -> None:
        self.received_packets.append(packet)

    def apply_learning(self, events: Iterable[Any]) -> Any:
        self.learn_calls.append(list(events))
        return {"ok": True}

    def generate_immune_report(self, **kwargs: Any) -> Dict[str, Any]:
        # Return deterministic structure; omit "text" for one test.
        return {"meta": kwargs, "text": "HELLO"}

    def threat_insights(self, min_severity: int = 0) -> str:
        return f"INSIGHTS:{min_severity}"

    def get_last_update_metadata(self) -> Dict[str, Any]:
        return {"last": "ok"}


def test_handle_event_ignores_non_dict():
    iface = AdaptiveCoreInterface(engine=_FakeEngine())
    iface.handle_event("not-a-dict")  # should not raise
    assert iface.list_events() == []


def test_handle_event_normalizes_and_preserves_extra_keys():
    iface = AdaptiveCoreInterface(engine=_FakeEngine())

    iface.handle_event(
        {
            "event_id": 123,          # will be str(...)
            "action": 999,            # will be str(...)
            "severity": "0.75",       # will be float(...)
            "fingerprint": "fp-x",
            "extra": {"a": 1},
        }
    )

    events = iface.list_events()
    assert len(events) == 1
    e = events[0]

    assert e["event_id"] == "123"
    assert e["action"] == "999"
    assert abs(e["severity"] - 0.75) < 1e-9
    assert e["fingerprint"] == "fp-x"
    assert e["extra"] == {"a": 1}

    # default source
    assert e["source"] == "external"


def test_handle_event_keeps_existing_source_and_defaults_missing_fields():
    iface = AdaptiveCoreInterface(engine=_FakeEngine())

    iface.handle_event({"source": "qwg"})
    e = iface.list_events()[0]

    assert e["source"] == "qwg"
    assert e["event_id"] == "unknown"
    assert e["action"] == "unknown"
    assert abs(e["severity"] - 0.0) < 1e-12


def test_list_events_returns_copy():
    iface = AdaptiveCoreInterface(engine=_FakeEngine())
    iface.handle_event({"event_id": "1"})
    a = iface.list_events()
    b = iface.list_events()
    assert a == b
    assert a is not b  # shallow copy


def test_read_only_wrappers_delegate_to_engine():
    eng = _FakeEngine()
    iface = AdaptiveCoreInterface(engine=eng)

    report = iface.get_immune_report(min_severity=2, pattern_window=3, trend_bucket="day", last_n=4)
    assert report["meta"]["min_severity"] == 2
    assert report["meta"]["pattern_window"] == 3
    assert report["meta"]["trend_bucket"] == "day"
    assert report["meta"]["last_n"] == 4

    assert iface.get_immune_report_text() == "HELLO"
    assert iface.get_threat_insights_text(min_severity=7) == "INSIGHTS:7"

    # state passthrough
    assert iface.get_adaptive_state() is eng.state
    assert iface.get_last_update_metadata() == {"last": "ok"}
