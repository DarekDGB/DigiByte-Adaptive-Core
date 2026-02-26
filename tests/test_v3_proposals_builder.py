from __future__ import annotations

import json
from pathlib import Path

import pytest

from adaptive_core.v3.proposals import build_upgrade_proposal_v3


def _repo_root() -> Path:
    # tests/ is at repo root/tests/
    return Path(__file__).resolve().parents[1]


def _load_template() -> dict:
    p = _repo_root() / "proposals" / "template" / "upgrade_proposal_v3.template.json"
    return json.loads(p.read_text(encoding="utf-8"))


def test_builder_seals_template_and_returns_canonical() -> None:
    proposal = _load_template()
    # Template contains placeholder hash — builder must compute correct one.
    proposal.pop("proposal_hash", None)

    sealed = build_upgrade_proposal_v3(proposal)

    assert sealed["v"] == "upgrade_proposal_v3"
    assert sealed["proposal_hash"]
    assert isinstance(sealed["evidence"], dict)
    assert isinstance(sealed["guardrails"], list)
    assert isinstance(sealed["changes"], list)

    # Canonical expectations: guardrails + changes are deterministic order
    assert sealed["guardrails"] == sorted(sealed["guardrails"])
    assert [c["change_id"] for c in sealed["changes"]] == sorted(c["change_id"] for c in sealed["changes"])


def test_builder_is_deterministic_for_same_input() -> None:
    proposal = _load_template()
    proposal.pop("proposal_hash", None)

    a = build_upgrade_proposal_v3(proposal)
    b = build_upgrade_proposal_v3(proposal)

    assert a == b
    assert a["proposal_hash"] == b["proposal_hash"]


def test_builder_denies_unknown_guardrail() -> None:
    proposal = _load_template()
    proposal.pop("proposal_hash", None)
    proposal["guardrails"] = ["AMG-999"]

    with pytest.raises(ValueError) as e:
        build_upgrade_proposal_v3(proposal)

    assert "AC_V3_GUARDRAIL_UNKNOWN" in str(e.value)

def test_builder_denies_non_mapping_input() -> None:
    with pytest.raises(ValueError) as e:
        # type: ignore[arg-type]
        build_upgrade_proposal_v3(["not", "a", "mapping"])
    assert "AC_V3_PROPOSAL_INVALID" in str(e.value)


def test_builder_normalizes_guardrails_and_sorts_changes() -> None:
    proposal = _load_template()
    proposal.pop("proposal_hash", None)

    # hit builder branches for guardrails list normalization
    proposal["guardrails"] = [" AMG-001 ", "AMG-001", "AMG-002"]

    # hit builder branches for sorting changes by change_id
    proposal["changes"] = [
        {"change_id": "B", "type": "modify", "detail": "second"},
        {"change_id": "A", "type": "add", "detail": "first"},
    ]

    sealed = build_upgrade_proposal_v3(proposal)

    assert sealed["guardrails"] == ["AMG-001", "AMG-002"]
    assert [c["change_id"] for c in sealed["changes"]] == ["A", "B"]
