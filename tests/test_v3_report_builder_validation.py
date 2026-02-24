import pytest

from adaptive_core.v3.correlation import CorrelationSnapshot
from adaptive_core.v3.drift import LayerContract
from adaptive_core.v3.evidence_store import EvidenceSnapshot
from adaptive_core.v3.report_builder import build_upgrade_report
from adaptive_core.v3.report_models import CapabilitiesV3


def _caps() -> CapabilitiesV3:
    return CapabilitiesV3(envelope="ABSENT", correlation="OFF", archival="OFF", telemetry="OFF")


def _empty_snapshot() -> EvidenceSnapshot:
    return EvidenceSnapshot(
        total_events=0,
        by_source_layer={},
        by_event_type={},
        by_upstream_reason_id={},
    )


def test_report_builder_rejects_invalid_report_id() -> None:
    with pytest.raises(ValueError) as e:
        build_upgrade_report(
            report_id="",
            target_layers=["DQSN"],
            snapshot=_empty_snapshot(),
            capabilities=_caps(),
        )
    assert "AC_V3_REPORT_INVALID" in str(e.value)
    assert "report_id" in str(e.value)


def test_report_builder_rejects_invalid_target_layers() -> None:
    with pytest.raises(ValueError) as e:
        build_upgrade_report(
            report_id="AC-UR-TEST-0001",
            target_layers=["", "DQSN"],
            snapshot=_empty_snapshot(),
            capabilities=_caps(),
        )
    assert "AC_V3_REPORT_INVALID" in str(e.value)
    assert "target_layers" in str(e.value)


def test_report_builder_rejects_invalid_drift_contracts_type() -> None:
    with pytest.raises(ValueError) as e:
        build_upgrade_report(
            report_id="AC-UR-TEST-0002",
            target_layers=["DQSN"],
            snapshot=_empty_snapshot(),
            capabilities=_caps(),
            drift_contracts="not-a-list",  # type: ignore[arg-type]
        )
    assert "AC_V3_REPORT_INVALID" in str(e.value)
    assert "drift_contracts" in str(e.value)


def test_report_builder_rejects_invalid_correlation_snapshot_type() -> None:
    with pytest.raises(ValueError) as e:
        build_upgrade_report(
            report_id="AC-UR-TEST-0003",
            target_layers=["DQSN"],
            snapshot=_empty_snapshot(),
            capabilities=_caps(),
            correlation_snapshot={"nope": True},  # type: ignore[arg-type]
            include_correlation=False,
        )
    assert "AC_V3_REPORT_INVALID" in str(e.value)
    assert "correlation_snapshot" in str(e.value)


def test_report_builder_include_correlation_requires_snapshot() -> None:
    with pytest.raises(ValueError) as e:
        build_upgrade_report(
            report_id="AC-UR-TEST-0004",
            target_layers=["DQSN"],
            snapshot=_empty_snapshot(),
            capabilities=_caps(),
            correlation_snapshot=None,
            include_correlation=True,
        )
    assert "AC_V3_REPORT_INVALID" in str(e.value)
    assert "include_correlation requires correlation_snapshot" in str(e.value)


def test_reproducibility_half_when_findings_exist_without_reason_id() -> None:
    # Create drift findings (their evidence does NOT contain "reason_id"),
    # while snapshot has zero events so generate_findings() returns empty.
    drift_contracts = [
        LayerContract(layer="DQSN", assumptions={"meta.canonical": "true"}),
        LayerContract(layer="QWG", assumptions={"meta.canonical": "false"}),
    ]

    r = build_upgrade_report(
        report_id="AC-UR-TEST-0005",
        target_layers=["DQSN"],
        snapshot=_empty_snapshot(),
        capabilities=_caps(),
        confidence_threshold=0.0,  # ensure UPGRADE_REPORT deterministically
        drift_contracts=drift_contracts,
        include_drift_graph=False,
        correlation_snapshot=CorrelationSnapshot(
            total_nodes=0,
            total_events=0,
            by_upstream_reason_id={},
            nodes_reporting_reason_id={},
        ),
        include_correlation=False,
    )

    assert r.confidence_breakdown["reproducibility"] == 0.5
