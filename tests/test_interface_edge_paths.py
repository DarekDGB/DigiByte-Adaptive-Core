from __future__ import annotations

from typing import Any, Dict, Iterable, List

from adaptive_core.interface import AdaptiveCoreInterface


class _FakeEngine:
    def __init__(self) -> None:
        self.received_packets: List[Any] = []
        self.learned_events: List[Any] = []

    def receive_threat_packet(self, packet: Any) -> None:
        self.received_packets.append(packet)

    def apply_learning(self, events: Iterable[Any]) -> str:
        self.learned_events.extend(list(events))
        return "OK"


def test_submit_threat_packet_calls_engine_receive() -> None:
    engine = _FakeEngine()
    iface = AdaptiveCoreInterface(engine=engine)

    pkt = object()
    iface.submit_threat_packet(pkt)

    assert engine.received_packets == [pkt]


def test_submit_feedback_events_calls_engine_apply_learning() -> None:
    engine = _FakeEngine()
    iface = AdaptiveCoreInterface(engine=engine)

    events = [object(), object()]
    result = iface.submit_feedback_events(events)

    assert result == "OK"
    assert engine.learned_events == events


def test_handle_event_non_dict_is_ignored() -> None:
    iface = AdaptiveCoreInterface()
    iface.handle_event("not-a-dict")  # type: ignore[arg-type]

    assert iface.list_events() == []


def test_handle_event_exception_is_swallowed_fail_closed() -> None:
    iface = AdaptiveCoreInterface()

    # This is a dict (so it passes the type check),
    # but severity conversion will raise ValueError inside try-block.
    bad: Dict[str, Any] = {"event_id": "e1", "action": "warn", "severity": "not-a-float"}
    iface.handle_event(bad)

    # Must not crash caller, and must not append a broken event.
    assert iface.list_events() == []
