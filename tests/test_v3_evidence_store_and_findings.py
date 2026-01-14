from adaptive_core.v3.canonicalize import canonicalize_event
from adaptive_core.v3.evidence_store import EvidenceStoreV3
from adaptive_core.v3.analyze import generate_findings, AnalyzeConfig


def _evt(reason_id: str, cid: str) -> dict:
    return {
        "source_layer": "dqsn",
        "event_type": "reject",
        "severity": 0.4,
        "timestamp": "2026-01-14T00:00:00Z",
        "correlation_id": cid,
        "meta": {},
        "reason_id": reason_id,
    }


def test_evidence_store_counts_and_eviction_are_deterministic():
    store = EvidenceStoreV3(max_events=3)

    store.add(canonicalize_event(_evt("R1", "c1")))
    store.add(canonicalize_event(_evt("R1", "c2")))
    store.add(canonicalize_event(_evt("R2", "c3")))

    snap = store.snapshot()
    assert snap.total_events == 3
    assert snap.by_upstream_reason_id == {"R1": 2, "R2": 1}

    # add one more -> oldest evicted (R1,c1)
    store.add(canonicalize_event(_evt("R2", "c4")))
    snap2 = store.snapshot()
    assert snap2.total_events == 3
    assert snap2.by_upstream_reason_id == {"R1": 1, "R2": 2}


def test_generate_findings_reason_spike():
    store = EvidenceStoreV3(max_events=100)

    # 10 events total, 5 share same reason -> meets defaults (min_count=5, min_ratio=0.10)
    for i in range(5):
        store.add(canonicalize_event(_evt("SPIKE", f"s{i}")))
    for i in range(5):
        store.add(canonicalize_event(_evt("OTHER", f"o{i}")))

    findings = generate_findings(store.snapshot(), AnalyzeConfig(reason_spike_min_count=5, reason_spike_min_ratio=0.10))
    assert any(f.finding_id == "AC-FIND-REASON-SPIKE::SPIKE" for f in findings)
