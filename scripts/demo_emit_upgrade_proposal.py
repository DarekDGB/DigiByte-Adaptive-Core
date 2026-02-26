from __future__ import annotations

from pathlib import Path

from adaptive_core.v3.trigger import maybe_propose_upgrade_from_findings


def main() -> None:
    demo_outbox = Path("_demo_outbox")
    demo_outbox.mkdir(parents=True, exist_ok=True)

    proposal = maybe_propose_upgrade_from_findings(
        findings=[{"drift_score": 0.80}],
        drift_threshold=0.50,
        proposal_id="AC-DEMO-0001",
        component="eqc_engine",
        version="3.1.0",
        created_utc="2026-02-26T00:00:00Z",
        outbox_dir=demo_outbox,
    )

    if proposal is None:
        raise SystemExit("Trigger did not fire (unexpected for demo).")

    print("DEMO PROPOSAL EMITTED")
    print("proposal_id:", proposal["proposal_id"])
    print("proposal_hash:", proposal["proposal_hash"])
    print("outbox_dir:", str(demo_outbox))


if __name__ == "__main__":
    main()
