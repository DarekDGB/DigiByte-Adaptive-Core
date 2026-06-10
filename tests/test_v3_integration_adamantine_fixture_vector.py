from __future__ import annotations

import json
from pathlib import Path

from adaptive_core.v3.integration.adamantine import build_adamantine_advisory_evidence_v1

FIXTURE = Path("tests/fixtures/adamantine/adaptive_core_adamantine_advisory_evidence_v1.json")
CTX = "a" * 64
NOW = 1_760_000_200


def test_adamantine_exporter_matches_shared_16e_fixture_vector() -> None:
    expected = json.loads(FIXTURE.read_text(encoding="utf-8"))

    actual = build_adamantine_advisory_evidence_v1(
        context_hash=CTX,
        issued_at=1_760_000_000,
        expires_at=1_760_003_600,
        generated_at=1_760_000_100,
        overall_score=91,
        now=NOW,
    )

    assert actual == expected
