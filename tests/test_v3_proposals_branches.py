from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

import adaptive_core.v3.proposals as proposals
from adaptive_core.v3.proposals import (
    compute_proposal_hash,
    load_json_file,
    validate_and_canonicalize_upgrade_proposal,
    validate_inbox,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_template() -> Dict[str, Any]:
    p = _repo_root() / "proposals" / "template" / "upgrade_proposal_v3.template.json"
    return json.loads(p.read_text(encoding="utf-8"))


def _finalize_hash_like_validator(proposal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute proposal_hash over the canonical form that the validator expects:
    - changes sorted by change_id
    - guardrails sorted/deduped
    - evidence defaults to {}
    - guardrails_ref defaults to ""
    """
    base = dict(proposal)
    base.pop("proposal_hash", None)

    # Evidence default
    if "evidence" not in base or base["evidence"] is None:
        base["evidence"] = {}

    # guardrails_ref default
    if "guardrails_ref" not in base or base["guardrails_ref"] is None:
        base["guardrails_ref"] = ""

    # Canonicalize guardrails if present
    if "guardrails" in base and isinstance(base["guardrails"], list):
        base["guardrails"] = sorted(set([str(x).strip() for x in base["guardrails"]]))

    # Canonicalize changes (only if entries look like dicts with change_id)
    if "changes" in base and isinstance(base["changes"], list):
        if all(isinstance(d, dict) and "change_id" in d for d in base["changes"]):
            base["changes"] = sorted(base["changes"], key=lambda d: d["change_id"])

    h = compute_proposal_hash(base)
    proposal["proposal_hash"] = h
    return proposal


def _valid_proposal() -> Dict[str, Any]:
    p = _load_template()
    return _finalize_hash_like_validator(p)


def test_repo_root_from_here_raises_when_no_proposals_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Force _repo_root_from_here() to search in a temp dir that has no "proposals/" anywhere above it.
    fake_file = tmp_path / "x.py"
    fake_file.write_text("# x", encoding="utf-8")
    monkeypatch.setattr(proposals, "__file__", str(fake_file))

    with pytest.raises(ValueError) as e:
        proposals._repo_root_from_here()  # type: ignore[attr-defined]

    assert "AC_V3_PROPOSAL_INVALID" in str(e.value)


def test_validate_inbox_passes_when_empty() -> None:
    # With only .gitkeep present, inbox has no *.json so validation should pass.
    validate_inbox()


def test_validate_inbox_fails_when_inbox_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Point repo root to a temp folder missing proposals/inbox.
    monkeypatch.setattr(proposals, "_repo_root_from_here", lambda: tmp_path)

    with pytest.raises(ValueError) as e:
        validate_inbox()

    assert "proposals/inbox missing" in str(e.value)


def test_validate_inbox_validates_a_real_json_file(tmp_path: Path) -> None:
    # Write a valid proposal into the real repo inbox, validate, then clean up.
    inbox = _repo_root() / "proposals" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)

    f = inbox / "TEST_VALID_PROPOSAL.json"
    f.write_text(json.dumps(_valid_proposal(), ensure_ascii=False), encoding="utf-8")

    try:
        validate_inbox()
    finally:
        f.unlink(missing_ok=True)


def test_load_json_file_invalid_json_fails(tmp_path: Path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("{not-json", encoding="utf-8")

    with pytest.raises(ValueError) as e:
        load_json_file(p)

    assert "invalid json" in str(e.value)


def test_load_json_file_non_object_fails(tmp_path: Path) -> None:
    p = tmp_path / "arr.json"
    p.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError) as e:
        load_json_file(p)

    assert "json root must be object" in str(e.value)


def test_validate_rejects_non_mapping_root() -> None:
    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(["nope"])  # type: ignore[arg-type]
    assert "proposal must be an object" in str(e.value)


def test_require_str_missing_field() -> None:
    proposal = _valid_proposal()
    proposal.pop("summary", None)
    proposal = _finalize_hash_like_validator(proposal)

    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(proposal)

    assert "AC_V3_MISSING_FIELD" in str(e.value)


def test_require_str_empty_string_rejected() -> None:
    proposal = _valid_proposal()
    proposal["summary"] = "   "
    proposal = _finalize_hash_like_validator(proposal)

    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(proposal)

    assert "AC_V3_TYPE_INVALID" in str(e.value)


def test_bad_v_rejected() -> None:
    proposal = _valid_proposal()
    proposal["v"] = "wrong"
    proposal = _finalize_hash_like_validator(proposal)

    with pytest.raises(ValueError):
        validate_and_canonicalize_upgrade_proposal(proposal)


def test_proposal_id_with_space_rejected() -> None:
    proposal = _valid_proposal()
    proposal["proposal_id"] = "AC UPG BAD"
    proposal = _finalize_hash_like_validator(proposal)

    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(proposal)

    assert "must not contain spaces" in str(e.value)


def test_target_not_object_rejected() -> None:
    proposal = _valid_proposal()
    proposal["target"] = []  # type: ignore[assignment]
    proposal = _finalize_hash_like_validator(proposal)

    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(proposal)

    assert "'target' must be object" in str(e.value)


def test_target_unknown_key_rejected() -> None:
    proposal = _valid_proposal()
    proposal["target"]["extra"] = "x"
    proposal = _finalize_hash_like_validator(proposal)

    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(proposal)

    assert "unknown keys in target" in str(e.value)


def test_timestamp_invalid_isoformat_rejected() -> None:
    proposal = _valid_proposal()
    proposal["created_utc"] = "2026-99-99T00:00:00Z"  # ends with Z but invalid date
    proposal = _finalize_hash_like_validator(proposal)

    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(proposal)

    assert "AC_V3_PROPOSAL_TIMESTAMP_INVALID" in str(e.value)


def test_changes_empty_rejected() -> None:
    proposal = _valid_proposal()
    proposal["changes"] = []
    proposal = _finalize_hash_like_validator(proposal)

    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(proposal)

    assert "'changes' must be non-empty list" in str(e.value)


def test_change_entry_not_object_rejected() -> None:
    proposal = _valid_proposal()
    proposal["changes"] = [123]  # type: ignore[list-item]

    # Do NOT finalize hash here — we want validator to fail earlier.
    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(proposal)

    assert "change entry must be object" in str(e.value)


def test_change_unknown_key_rejected() -> None:
    proposal = _valid_proposal()
    proposal["changes"][0]["extra"] = "x"
    proposal = _finalize_hash_like_validator(proposal)

    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(proposal)

    assert "unknown keys in change" in str(e.value)


def test_change_bad_type_rejected() -> None:
    proposal = _valid_proposal()
    proposal["changes"][0]["type"] = "hack"
    proposal = _finalize_hash_like_validator(proposal)

    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(proposal)

    assert "bad change.type" in str(e.value)


def test_duplicate_change_id_rejected() -> None:
    proposal = _valid_proposal()
    proposal["changes"].append(dict(proposal["changes"][0]))
    proposal = _finalize_hash_like_validator(proposal)

    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(proposal)

    assert "duplicate change_id" in str(e.value)


def test_evidence_wrong_type_rejected() -> None:
    proposal = _valid_proposal()
    proposal["evidence"] = []  # type: ignore[assignment]
    proposal = _finalize_hash_like_validator(proposal)

    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(proposal)

    assert "'evidence' must be object" in str(e.value)


def test_guardrails_none_hits_empty_branch() -> None:
    proposal = _load_template()
    proposal.pop("guardrails", None)

    # Force the same canonical outcome as validator: guardrails becomes [].
    proposal["guardrails"] = []

    proposal = _finalize_hash_like_validator(proposal)

    res = validate_and_canonicalize_upgrade_proposal(proposal)
    assert res.canonical["guardrails"] == []


def test_guardrails_not_list_rejected() -> None:
    proposal = _valid_proposal()
    proposal["guardrails"] = "AMG-001"  # type: ignore[assignment]
    proposal = _finalize_hash_like_validator(proposal)

    with pytest.raises(ValueError):
        validate_and_canonicalize_upgrade_proposal(proposal)


def test_guardrails_element_not_str_rejected() -> None:
    proposal = _valid_proposal()
    proposal["guardrails"] = ["AMG-001", 123]  # type: ignore[list-item]
    proposal = _finalize_hash_like_validator(proposal)

    with pytest.raises(ValueError):
        validate_and_canonicalize_upgrade_proposal(proposal)


def test_guardrails_ref_invalid_type_rejected() -> None:
    proposal = _valid_proposal()
    proposal["guardrails_ref"] = 123  # type: ignore[assignment]
    proposal = _finalize_hash_like_validator(proposal)

    with pytest.raises(ValueError):
        validate_and_canonicalize_upgrade_proposal(proposal)


def test_proposal_hash_invalid_format_rejected() -> None:
    proposal = _valid_proposal()
    proposal["proposal_hash"] = "A" * 64  # uppercase not allowed by validator

    with pytest.raises(ValueError) as e:
        validate_and_canonicalize_upgrade_proposal(proposal)

    assert "AC_V3_PROPOSAL_HASH_INVALID" in str(e.value)


def test_canonicalization_sorts_changes_and_guardrails() -> None:
    proposal = _load_template()
    # unsorted + dup guardrails, unsorted changes
    proposal["guardrails"] = ["AMG-011", "AMG-001", "AMG-001"]
    proposal["changes"] = [
        {"change_id": "CHG-002", "type": "modify", "detail": "b"},
        {"change_id": "CHG-001", "type": "modify", "detail": "a"},
    ]
    proposal = _finalize_hash_like_validator(proposal)

    res = validate_and_canonicalize_upgrade_proposal(proposal)
    assert res.canonical["guardrails"] == ["AMG-001", "AMG-011"]
    assert [c["change_id"] for c in res.canonical["changes"]] == ["CHG-001", "CHG-002"]

def test_guardrails_explicit_none_hits_branch() -> None:
    proposal = _load_template()

    # Explicit None must hit proposals.py line 86 (guardrails is None -> gids = []).
    proposal["guardrails"] = None  # type: ignore[assignment]

    # Compute proposal_hash the same way the validator does:
    # it hashes the canonical form where guardrails becomes [].
    base = dict(proposal)
    base.pop("proposal_hash", None)

    if "evidence" not in base or base["evidence"] is None:
        base["evidence"] = {}
    if "guardrails_ref" not in base or base["guardrails_ref"] is None:
        base["guardrails_ref"] = ""

    # Canonical outcome for guardrails=None is [] (this is the branch we’re covering).
    base["guardrails"] = []

    # Canonical changes ordering
    base["changes"] = sorted(base["changes"], key=lambda d: d["change_id"])

    proposal["proposal_hash"] = compute_proposal_hash(base)

    res = validate_and_canonicalize_upgrade_proposal(proposal)
    assert res.canonical["guardrails"] == []
