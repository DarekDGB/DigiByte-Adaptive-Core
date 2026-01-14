from adaptive_core.memory_writer import AdaptiveMemoryWriter, InMemoryEventSink


def test_in_memory_event_sink_stores_events_in_order():
    sink = InMemoryEventSink()
    assert sink.events == []

    sink.store_event({"type": "t1", "value": 1})
    sink.store_event({"type": "t2", "value": 2})

    assert len(sink.events) == 2
    assert sink.events[0]["type"] == "t1"
    assert sink.events[1]["type"] == "t2"


def test_writer_write_from_dict_accepts_adaptive_event_and_stores_it():
    """
    AdaptiveEvent requires 'severity' (per failure output).
    """
    sink = InMemoryEventSink()
    writer = AdaptiveMemoryWriter(sink=sink)

    writer.write_from_dict(
        {
            "layer": "sentinel",
            "anomaly_type": "entropy_drop",
            "severity": 1,
        }
    )

    assert len(sink.events) == 1

    stored = sink.events[0]
    # stored may be a dataclass or dict depending on implementation; accept both
    if isinstance(stored, dict):
        assert stored.get("layer") == "sentinel"
        assert stored.get("anomaly_type") == "entropy_drop"
        assert int(stored.get("severity")) == 1
    else:
        assert getattr(stored, "layer") == "sentinel"
        assert getattr(stored, "anomaly_type") == "entropy_drop"
        assert int(getattr(stored, "severity")) == 1


def test_writer_write_from_dict_rejects_unknown_fields_fail_closed():
    sink = InMemoryEventSink()
    writer = AdaptiveMemoryWriter(sink=sink)

    try:
        writer.write_from_dict(
            {
                "layer": "sentinel",
                "anomaly_type": "x",
                "severity": 1,
                "payload": {"no": "thanks"},
            }
        )
        assert False, "expected TypeError for unknown field"
    except TypeError as e:
        assert "unexpected" in str(e).lower()
