import json
from pathlib import Path

import pytest

from adaptive_core.v3.integration.adamantine import (
    ADAMANTINE_ADVISORY_EVIDENCE_VERSION,
    build_adamantine_advisory_evidence_v1,
    validate_adamantine_advisory_evidence_v1,
)

CTX = "a" * 64
FIXTURE = Path("tests/fixtures/adamantine/adaptive_core_adamantine_advisory_evidence_v1.json")


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
        (_payload(signals=[{"source": "adaptive-core", "severity": 5, "reason_ids": ["ok"], "authority": True}]), "unknown fields"),
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

    with pytest.raises(ValueError, match=r"signals\[0\]\.reason_ids must be a non-empty string"):
        validate_adamantine_advisory_evidence_v1(payload)


@pytest.mark.parametrize(
    "unknown_field",
    [
        "shield_receipt",
        "signature",
        "signatures",
        "algorithm",
        "algorithm_family",
        "standard_profile",
        "profile",
        "key_id",
        "key_role",
        "decision",
        "verdict",
        "required_policy",
        "ml_dsa",
        "fn_dsa",
        "Authority",
        "AUTHORITY",
        "Final_Approval",
        "final-approval",
        "grantExecution",
        "Override",
        "Decision",
    ],
)
def test_signal_objects_reject_every_unknown_or_authority_looking_field(unknown_field):
    signal = {"source": "adaptive-core", "severity": 5, "reason_ids": ["ok"], unknown_field: "hostile"}

    with pytest.raises(ValueError, match=r"signals\[0\] unknown fields"):
        validate_adamantine_advisory_evidence_v1(_payload(signals=[signal]))


@pytest.mark.parametrize("missing_field", ["source", "severity", "reason_ids"])
def test_signal_objects_require_the_exact_field_set(missing_field):
    signal = {"source": "adaptive-core", "severity": 5, "reason_ids": ["ok"]}
    del signal[missing_field]

    with pytest.raises(ValueError, match=rf"signals\[0\]\.{missing_field}"):
        validate_adamantine_advisory_evidence_v1(_payload(signals=[signal]))


def test_tuple_signals_cannot_bypass_exact_field_validation():
    signal = {"source": "adaptive-core", "severity": 5, "reason_ids": ["ok"], "authority": True}

    with pytest.raises(ValueError, match=r"signals\[0\] unknown fields"):
        validate_adamantine_advisory_evidence_v1(_payload(signals=(signal,)))


@pytest.mark.parametrize(
    "bad_payload",
    [
        {**_payload(), "extra": "x", 1: "x"},
        {**_payload(), 1: "x"},
        _payload(
            signals=[
                {"source": "adaptive-core", "severity": 5, "reason_ids": ["ok"], "extra": "x", 1: "x"}
            ]
        ),
    ],
)
def test_non_string_and_mixed_unknown_keys_raise_the_contract_error(bad_payload):
    with pytest.raises(ValueError, match=r"AC_V3_REPORT_INVALID: .*unknown fields"):
        validate_adamantine_advisory_evidence_v1(bad_payload)


@pytest.mark.parametrize("field", ["issued_at", "expires_at", "generated_at", "overall_score"])
@pytest.mark.parametrize("boolean", [False, True])
def test_boolean_root_integer_fields_are_rejected(field, boolean):
    with pytest.raises(ValueError, match=rf"{field} must be an integer"):
        validate_adamantine_advisory_evidence_v1(_payload(**{field: boolean}))


@pytest.mark.parametrize("boolean", [False, True])
def test_boolean_signal_severity_is_rejected(boolean):
    signal = {"source": "adaptive-core", "severity": boolean, "reason_ids": ["ok"]}

    with pytest.raises(ValueError, match=r"signals\[0\]\.severity must be an integer"):
        validate_adamantine_advisory_evidence_v1(_payload(signals=[signal]))


@pytest.mark.parametrize("boolean", [False, True])
def test_boolean_now_is_rejected_by_validator_and_builder(boolean):
    with pytest.raises(ValueError, match="now must be an integer"):
        validate_adamantine_advisory_evidence_v1(_payload(), now=boolean)

    with pytest.raises(ValueError, match="now must be an integer"):
        build_adamantine_advisory_evidence_v1(
            context_hash=CTX,
            issued_at=900,
            expires_at=1_200,
            generated_at=950,
            overall_score=91,
            now=boolean,
        )


def test_cyclic_malformed_reason_ids_raise_the_contract_error():
    cyclic_reason_ids = []
    cyclic_reason_ids.append(cyclic_reason_ids)
    payload = _payload(
        signals=[{"source": "adaptive-core", "severity": 5, "reason_ids": cyclic_reason_ids}]
    )

    with pytest.raises(ValueError, match=r"AC_V3_REPORT_INVALID: signals\[0\]\.reason_ids"):
        validate_adamantine_advisory_evidence_v1(payload)


def test_builder_dealiases_custom_signal_input():
    reason_ids = ["ok"]
    signal = {"source": "adaptive-core", "severity": 10, "reason_ids": reason_ids}
    signals = [signal]

    payload = build_adamantine_advisory_evidence_v1(
        context_hash=CTX,
        issued_at=900,
        expires_at=1_200,
        generated_at=950,
        overall_score=88,
        signals=signals,
    )
    signal["severity"] = 99
    reason_ids[0] = "changed"
    signals.clear()

    assert payload["signals"] == [{"source": "adaptive-core", "severity": 10, "reason_ids": ["ok"]}]


def test_builder_preserves_shared_fixture_bytes():
    payload = build_adamantine_advisory_evidence_v1(
        context_hash=CTX,
        issued_at=1_760_000_000,
        expires_at=1_760_003_600,
        generated_at=1_760_000_100,
        overall_score=91,
        now=1_760_000_200,
    )

    assert (json.dumps(payload, indent=2) + "\n").encode("utf-8") == FIXTURE.read_bytes()


def test_validation_enforces_canonical_context_hash() -> None:
    with pytest.raises(ValueError, match="context_hash must be lowercase 64-character hex"):
        validate_adamantine_advisory_evidence_v1(_payload(context_hash="A" * 64))

    with pytest.raises(ValueError, match="context_hash must be lowercase 64-character hex"):
        validate_adamantine_advisory_evidence_v1(_payload(context_hash="not-a-hex-context"))


def test_validation_enforces_time_window_when_now_is_provided() -> None:
    with pytest.raises(ValueError, match="issued_at cannot be in the future"):
        validate_adamantine_advisory_evidence_v1(_payload(issued_at=1_001, expires_at=1_200), now=1_000)

    with pytest.raises(ValueError, match="expires_at cannot be in the past"):
        validate_adamantine_advisory_evidence_v1(_payload(issued_at=900, expires_at=999), now=1_000)

    with pytest.raises(ValueError, match="generated_at cannot be in the future"):
        validate_adamantine_advisory_evidence_v1(_payload(generated_at=1_001), now=1_000)


def test_builder_enforces_time_window_when_now_is_provided() -> None:
    payload = build_adamantine_advisory_evidence_v1(
        context_hash=CTX,
        issued_at=900,
        expires_at=1_200,
        generated_at=950,
        overall_score=91,
        now=1_000,
    )

    assert payload["context_hash"] == CTX


def test_validation_rejects_non_integer_now_when_provided() -> None:
    with pytest.raises(ValueError, match="now must be an integer"):
        validate_adamantine_advisory_evidence_v1(_payload(), now="1000")  # type: ignore[arg-type]
