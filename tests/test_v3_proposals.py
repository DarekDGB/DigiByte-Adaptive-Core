from __future__ import annotations

import json
from pathlib import Path

import pytest

from adaptive_core.v3.proposals import (
    compute_proposal_hash,
    validate_and_canonicalize_upgrade_proposal,
)


def _repo_root() -> Path:
    # tests/ is at repo_root/tests
    return Path(__file__).resolve().parents[1]


def _load_template() -> dict:
    p = _repo_root() / "proposals" / "template" / "upgrade_proposal_v3.template.json"
    return json.loads(p.read_text(encoding="utf-8"))


def _finalize_hash(proposal: dict) -> dict:
    # Build canonical-like object WITHOUT proposal_hash, matching validator canonical keys.
    # This mirrors how AdamantineOS will prepare proposals.
    base = dict(proposal)
    base.pop("proposal_hash", None)

    # Evidence must exist (validator defaults to {})
    if "evidence" not in base or base["evidence"] is None:
        base["evidence"] = {}

    # guardrails_ref must exist (validator uses "" if absent)
    if "guardrails_ref" not in base or base["guardrails_ref"] is None:
        base["guardrails_ref"] = ""

    # Deterministic sort/dedupe guardrails
    if "guardrails" in base and isinstance(base["guardrails"], list):
        base["guardrails"] = sorted(set([str(x).strip() for x in base["guardrails"]]))

    # Deterministic sort changes by change_id
    base["changes"] = sorted(base["changes"], key=lambda d: d["change_id"])

    h = compute_proposal_hash(base)
    proposal["proposal_hash"] = h
    return proposal


def test_template_is_valid_when_hash_is_correct() -> None:
    proposal = _load_template()
    proposal = _finalize_hash(proposal)

    res = validate_and_canonicalize_upgrade_proposal(proposal)
    assert res.computed_hash == proposal["proposal_hash"]


def test_unknown_guardrail_fails_closed() -> None:
    proposal = _finalize_hash(_load_template())
    proposal["guardrails"] = ["AMG-999"]  # not in registry
    proposal = _finalize_hash(proposal)

    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(proposal)

    assert "AC_V3_GUARDRAIL_UNKNOWN" in str(e.value)


def test_bad_timestamp_fails_closed() -> None:
    proposal = _finalize_hash(_load_template())
    proposal["created_utc"] = "2026-02-24T00:00:00"  # missing Z
    proposal = _finalize_hash(proposal)

    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(proposal)

    assert "AC_V3_PROPOSAL_TIMESTAMP_INVALID" in str(e.value)


def test_hash_mismatch_fails_closed() -> None:
    proposal = _finalize_hash(_load_template())
    proposal["proposal_hash"] = "0" * 64  # wrong

    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(proposal)

    assert "AC_V3_PROPOSAL_HASH_INVALID" in str(e.value)


def test_unknown_root_key_fails_closed() -> None:
    proposal = _finalize_hash(_load_template())
    proposal["extra"] = "nope"  # additionalProperties = false
    proposal = _finalize_hash(proposal)

    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(proposal)

    assert "AC_V3_PROPOSAL_INVALID" in str(e.value)
