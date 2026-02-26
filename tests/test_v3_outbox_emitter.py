from __future__ import annotations

import json
from pathlib import Path

import pytest

from adaptive_core.v3.outbox import emit_upgrade_proposal_v3_to_outbox
from adaptive_core.v3.proposals import build_upgrade_proposal_v3


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_template() -> dict:
    p = _repo_root() / "proposals" / "template" / "upgrade_proposal_v3.template.json"
    return json.loads(p.read_text(encoding="utf-8"))


def test_outbox_emitter_writes_file_and_is_idempotent(tmp_path: Path) -> None:
    raw = _load_template()
    raw.pop("proposal_hash", None)

    sealed = build_upgrade_proposal_v3(raw)

    outbox = tmp_path / "outbox"
    outbox.mkdir()

    p1 = emit_upgrade_proposal_v3_to_outbox(sealed, outbox_dir=outbox)
    assert p1.exists()

    # idempotent
    p2 = emit_upgrade_proposal_v3_to_outbox(sealed, outbox_dir=outbox)
    assert p2 == p1

    # content is canonical json
    data = json.loads(p1.read_text(encoding="utf-8"))
    assert data == sealed


def test_outbox_emitter_denies_missing_outbox_dir(tmp_path: Path) -> None:
    raw = _load_template()
    raw.pop("proposal_hash", None)
    sealed = build_upgrade_proposal_v3(raw)

    missing = tmp_path / "nope"

    with pytest.raises(ValueError) as e:
        emit_upgrade_proposal_v3_to_outbox(sealed, outbox_dir=missing)

    assert "AC_V3_PROPOSAL_INVALID" in str(e.value)


def test_outbox_emitter_denies_collision_with_different_content(tmp_path: Path) -> None:
    raw = _load_template()
    raw.pop("proposal_hash", None)
    sealed = build_upgrade_proposal_v3(raw)

    outbox = tmp_path / "outbox"
    outbox.mkdir()

    p1 = emit_upgrade_proposal_v3_to_outbox(sealed, outbox_dir=outbox)

    # Corrupt file content to simulate collision
    p1.write_text('{"corrupt":true}\n', encoding="utf-8")

    with pytest.raises(ValueError) as e:
        emit_upgrade_proposal_v3_to_outbox(sealed, outbox_dir=outbox)

    assert "AC_V3_PROPOSAL_INVALID" in str(e.value)
