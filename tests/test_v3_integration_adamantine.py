import pytest

from adaptive_core.v3.integration.adamantine import (
    ADAMANTINE_ADVISORY_EVIDENCE_VERSION,
    build_adamantine_advisory_evidence_v1,
    validate_adamantine_advisory_evidence_v1,
)

CTX = "a" * 64


def _payload(**updates):
    payload = build_adamantine_advisory_evidence_v1(
        context_hash=CTX,
        issued_at=900,
        expires_at=1_200,
        generated_at=950,
        overall_score=91,
    )
    payload.update(updates)
    return payload


def test_builds_adamantineos_consumable_advisory_evidence_only():
    payload = build_adamantine_advisory_evidence_v1(
        context_hash=CTX,
        issued_at=900,
        expires_at=1_200,
        generated_at=950,
        overall_score=91,
    )

    assert payload == {
        "ac_iface_version": ADAMANTINE_ADVISORY_EVIDENCE_VERSION,
        "context_hash": CTX,
        "issued_at": 900,
        "expires_at": 1_200,
        "generated_at": 950,
        "overall_score": 91,
        "signals": [{"source": "adaptive-core", "severity": 5, "reason_ids": ["ok"]}],
        "oracle_version": "adaptive-core/3.0.0",
        "external_source_id": "adaptive-core-v3-adamantine-export",
    }
    assert "final_approval" not in payload
    assert "handoff_allowed" not in payload
    assert "authority" not in payload


def test_build_accepts_custom_signal_and_optional_source_metadata():
    payload = build_adamantine_advisory_evidence_v1(
        context_hash=CTX,
        issued_at=900,
        expires_at=1_200,
        generated_at=950,
        overall_score=88,
        signals=[{"source": "adaptive-core", "severity": 10, "reason_ids": ["ok"]}],
        oracle_version="adaptive-core/3.0.0-test",
        external_source_id="report-1",
    )

    assert payload["signals"][0]["severity"] == 10
    assert payload["oracle_version"] == "adaptive-core/3.0.0-test"
    assert payload["external_source_id"] == "report-1"


@pytest.mark.parametrize(
    "bad_payload, message",
    [
        ([], "payload must be an object"),
        (_payload(extra="x"), "unknown fields"),
        (_payload(final_approval=True), "unknown fields"),
        (_payload(signals=[{"source": "adaptive-core", "severity": 5, "reason_ids": ["ok"], "authority": True}]), "authority fields are forbidden"),
        (_payload(ac_iface_version="wrong"), "ac_iface_version must be"),
        (_payload(context_hash=""), "context_hash must be"),
        (_payload(issued_at="900"), "issued_at must be an integer"),
        (_payload(expires_at=899), "expires_at must be"),
        (_payload(generated_at=0), "generated_at must be positive"),
        (_payload(overall_score=101), "overall_score must be"),
        (_payload(oracle_version=""), "oracle_version must be"),
        (_payload(external_source_id=""), "external_source_id must be"),
        (_payload(signals=[]), "signals must be"),
        (_payload(signals=["bad"]), r"signals\[0\] must be"),
        (_payload(signals=[{"source": "", "severity": 5, "reason_ids": ["ok"]}]), r"signals\[0\]\.source must be"),
        (_payload(signals=[{"source": "adaptive-core", "severity": "5", "reason_ids": ["ok"]}]), r"signals\[0\]\.severity must be"),
        (_payload(signals=[{"source": "adaptive-core", "severity": 101, "reason_ids": ["ok"]}]), r"signals\[0\]\.severity must be"),
        (_payload(signals=[{"source": "adaptive-core", "severity": 5, "reason_ids": []}]), r"signals\[0\]\.reason_ids must be"),
        (_payload(signals=[{"source": "adaptive-core", "severity": 5, "reason_ids": [""]}]), r"signals\[0\]\.reason_ids must be"),
    ],
)
def test_validation_fails_closed_for_malformed_or_authority_payloads(bad_payload, message):
    with pytest.raises(ValueError, match=message):
        validate_adamantine_advisory_evidence_v1(bad_payload)  # type: ignore[arg-type]


def test_nested_authority_field_denies_when_root_key_is_allowed():
    payload = _payload(signals=[{"source": "adaptive-core", "severity": 5, "reason_ids": ["ok", {"override": True}]}])

    with pytest.raises(ValueError, match="authority fields are forbidden"):
        validate_adamantine_advisory_evidence_v1(payload)
