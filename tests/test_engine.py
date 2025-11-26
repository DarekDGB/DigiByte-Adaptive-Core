# tests/test_engine.py

from adaptive_core.engine import AdaptiveEngine
from adaptive_core.models import (
    RiskEvent,
    FeedbackType,
    AdaptiveState,
)


def make_event(
    event_id: str,
    layer: str,
    feedback: FeedbackType,
    risk_score: float = 0.8,
    risk_level: str = "high",
) -> RiskEvent:
    return RiskEvent(
        event_id=event_id,
        layer=layer,
        risk_score=risk_score,
        risk_level=risk_level,
        feedback=feedback,
    )


def test_true_positive_increases_weight_and_threshold():
    engine = AdaptiveEngine(initial_state=AdaptiveState(layer_weights={"sentinel": 1.0}))

    e = make_event("e1", "sentinel", FeedbackType.TRUE_POSITIVE)
    engine.record_events([e])
    result = engine.apply_learning([e])

    assert result.state.layer_weights["sentinel"] > 1.0
    assert result.state.global_threshold > 0.5


def test_false_positive_decreases_weight_and_threshold():
    engine = AdaptiveEngine(initial_state=AdaptiveState(layer_weights={"adn": 1.0}))

    e = make_event("e2", "adn", FeedbackType.FALSE_POSITIVE)
    engine.record_events([e])
    result = engine.apply_learning([e])

    assert result.state.layer_weights["adn"] < 1.0
    assert result.state.global_threshold < 0.5


def test_missed_attack_strengthens_all_layers():
    engine = AdaptiveEngine(
        initial_state=AdaptiveState(layer_weights={"sentinel": 1.0, "dqs": 1.0})
    )

    e = make_event("e3", "qwg", FeedbackType.MISSED_ATTACK)
    engine.record_events([e])
    result = engine.apply_learning([e])

    assert result.state.layer_weights["sentinel"] > 1.0
    assert result.state.layer_weights["dqs"] > 1.0
    assert result.state.global_threshold > 0.5
