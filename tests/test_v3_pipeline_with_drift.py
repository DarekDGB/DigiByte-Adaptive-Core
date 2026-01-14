from adaptive_core.v3.drift import LayerContract
from adaptive_core.v3.evidence_store import EvidenceSnapshot
from adaptive_core.v3.pipeline import run_v3_pipeline
from adaptive_core.v3.report_models import CapabilitiesV3


def test_pipeline_includes_drift_findings_and_optional_dot_graph():
    snap = EvidenceSnapshot(
        total_events=10,
        by_source_layer={"dqsn": 10},
        by_event_type={"reject": 10},
        by_upstream_reason_id={"SPIKE": 10},
    )

    contracts = [
        LayerContract(layer="Sentinel", assumptions={"meta.canonical": "true"}),
        LayerContract(layer="DQSN", assumptions={"meta.canonical": "false"}),
    ]

    caps = CapabilitiesV3(envelope="ABSENT", correlation="OFF", archival="OFF", telemetry="OFF")

    _, json_text, md_text, env = run_v3_pipeline(
        report_id="AC-UR-STEP8-0001",
        target_layers=["Sentinel", "DQSN"],
        snapshot=snap,
        confidence_threshold=0.0,  # force upgrade report
        capabilities=caps,
        drift_contracts=contracts,
        include_drift_graph=True,
    )

    assert "AC-DRIFT::meta.canonical" in json_text
    assert "digraph DriftRadar" in md_text
    assert env.report_hash  # non-empty
