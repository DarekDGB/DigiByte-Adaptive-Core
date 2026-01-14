from adaptive_core.memory_writer import AdaptiveMemoryWriter, InMemoryEventSink


def test_in_memory_event_sink_stores_events_in_order():
    sink = InMemoryEventSink()
    assert sink.events == []

    sink.store_event({"type": "t1", "value": 1})
    sink.store_event({"type": "t2", "value": 2})

    assert len(sink.events) == 2
    assert sink.events[0]["type"] == "t1"
    assert sink.events[1]["type"] == "t2"


def test_writer_write_event_appends_to_sink():
    sink = InMemoryEventSink()
    writer = AdaptiveMemoryWriter(sink=sink)

    writer.write_event(event_type="alpha", payload={"x": 1})
    writer.write_event(event_type="beta", payload={"y": 2})

    assert len(sink.events) == 2
    assert sink.events[0]["event_type"] == "alpha"
    assert sink.events[0]["payload"] == {"x": 1}
    assert sink.events[1]["event_type"] == "beta"
    assert sink.events[1]["payload"] == {"y": 2}


def test_writer_write_from_dict_requires_type_key():
    sink = InMemoryEventSink()
    writer = AdaptiveMemoryWriter(sink=sink)

    # missing "event_type" should raise
    try:
        writer.write_from_dict({"payload": {"x": 1}})
        assert False, "expected ValueError"
    except ValueError as e:
        assert "event_type" in str(e).lower()


def test_writer_write_from_dict_accepts_full_event():
    sink = InMemoryEventSink()
    writer = AdaptiveMemoryWriter(sink=sink)

    writer.write_from_dict({"event_type": "gamma", "payload": {"z": 9}})
    assert len(sink.events) == 1
    assert sink.events[0]["event_type"] == "gamma"
    assert sink.events[0]["payload"] == {"z": 9}
