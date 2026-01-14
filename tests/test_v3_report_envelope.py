from adaptive_core.v3.evidence_store import EvidenceSnapshot
from adaptive_core.v3.report_builder import build_upgrade_report, render_report_json
from adaptive_core.v3.report_models import CapabilitiesV3
from adaptive_core.v3.envelope import create_report_envelope


def test_report_envelope_hash_is_deterministic():
    snap = EvidenceSnapshot(
        total_events=10,
        by_source_layer={"dqsn": 10},
        by_event_type={"reject": 10},
        by_upstream_reason_id={"SPIKE": 10},
    )

    report = build_upgrade_report(
        report_id="AC-UR-2026-STEP5",
        target_layers=["DQSN"],
        snapshot=snap,
        capabilities=CapabilitiesV3(
            envelope="ABSENT",
            correlation="OFF",
            archival="OFF",
            telemetry="OFF",
        ),
        confidence_threshold=0.0,  # force upgrade report
    )

    json1 = render_report_json(report)
    json2 = render_report_json(report)

    env1 = create_report_envelope(report=report, canonical_json=json1)
    env2 = create_report_envelope(report=report, canonical_json=json2)

    assert env1.report_hash == env2.report_hash
    assert env1.classical_signature == "ABSENT"
    assert env1.pqc_signature == "ABSENT"
