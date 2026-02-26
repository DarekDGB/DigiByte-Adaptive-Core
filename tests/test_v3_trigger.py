from __future__ import annotations

from pathlib import Path

from adaptive_core.v3.trigger import maybe_propose_upgrade_from_findings


def test_trigger_returns_none_when_not_triggered(tmp_path: Path) -> None:
    outbox = tmp_path / "outbox"
    outbox.mkdir()

    findings = [
        {"drift_score": 0.10},
        {"drift_score": 0.49},
    ]

    res = maybe_propose_upgrade_from_findings(
        findings=findings,
        drift_threshold=0.50,
        proposal_id="AC-TRIGGER-001",
        component="eqc_engine",
        version="3.1.0",
        created_utc="2026-02-26T00:00:00Z",
        outbox_dir=outbox,
    )

    assert res is None
    assert list(outbox.glob("*.json")) == []


def test_trigger_emits_outbox_artifact_and_returns_canonical(tmp_path: Path) -> None:
    outbox = tmp_path / "outbox"
    outbox.mkdir()

    findings = [
        {"drift_score": 0.25},
        {"drift_score": 0.80},
    ]

    res = maybe_propose_upgrade_from_findings(
        findings=findings,
        drift_threshold=0.50,
        proposal_id="AC-TRIGGER-002",
        component="eqc_engine",
        version="3.1.0",
        created_utc="2026-02-26T00:00:00Z",
        outbox_dir=outbox,
    )

    assert res is not None
    assert res["v"] == "upgrade_proposal_v3"
    assert res["proposal_id"] == "AC-TRIGGER-002"
    assert res["target"]["component"] == "eqc_engine"
    assert res["target"]["version"] == "3.1.0"
    assert res["created_utc"] == "2026-02-26T00:00:00Z"
    assert res["proposal_hash"]
    assert res["guardrails"] == ["AMG-001"]

    files = sorted(outbox.glob("*.json"))
    assert len(files) == 1

    emitted_text = files[0].read_text(encoding="utf-8")
    assert res["proposal_hash"] in emitted_text


def test_trigger_uses_max_drift_in_summary(tmp_path: Path) -> None:
    outbox = tmp_path / "outbox"
    outbox.mkdir()

    findings = [
        {"drift_score": 0.51},
        {"drift_score": 0.77},
        {"drift_score": 0.60},
    ]

    res = maybe_propose_upgrade_from_findings(
        findings=findings,
        drift_threshold=0.50,
        proposal_id="AC-TRIGGER-003",
        component="eqc_engine",
        version="3.1.0",
        created_utc="2026-02-26T00:00:00Z",
        outbox_dir=outbox,
    )

    assert res is not None
    # max drift is 0.77 → formatted to 4dp
    assert "0.7700" in res["summary"]
    assert "0.5000" in res["summary"]
