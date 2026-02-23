import pytest
from adaptive_core.interface import AdaptiveCoreInterface


def test_interface_handles_none_input():
    iface = AdaptiveCoreInterface()

    result = iface.process_event(None)

    assert result is None


def test_interface_handles_empty_dict():
    iface = AdaptiveCoreInterface()

    result = iface.process_event({})

    assert result is not None


def test_interface_invalid_type():
    iface = AdaptiveCoreInterface()

    result = iface.process_event("invalid")

    assert result is None
