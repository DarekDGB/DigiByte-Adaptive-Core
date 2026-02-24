from __future__ import annotations

from adaptive_core.models import AdaptiveState


def test_adaptive_state_normalised_weights_empty() -> None:
    s = AdaptiveState(layer_weights={})
    assert s.normalised_weights() == {}


def test_adaptive_state_normalised_weights_normalizes() -> None:
    s = AdaptiveState(layer_weights={"a": 2.0, "b": 1.0})
    out = s.normalised_weights()
    assert out["a"] == 2.0 / 3.0
    assert out["b"] == 1.0 / 3.0
