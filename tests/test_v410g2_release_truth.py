from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
import re
import tomllib

from adaptive_core.v3.integration.adamantine import (
    ADAMANTINE_ADVISORY_EVIDENCE_VERSION,
    build_adamantine_advisory_evidence_v1,
)


ROOT = Path(__file__).resolve().parents[1]
STATUS = "docs/RELEASE_STATUS_V4_10_G2.md"
COPY_PATHS = (
    "CHANGELOG.md",
    STATUS,
    "tests/test_v410g2_release_truth.py",
    "pyproject.toml",
    "README.md",
    "SECURITY.md",
    "docs/reports/INDEX.md",
    "docs/reports/v3/INDEX.md",
    "docs/reports/v3/README.md",
    "docs/reports/v3/ADAMANTINEOS_INTEGRATION.md",
    "tests/test_v49c_documentation_alignment.py",
)


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_g2_package_and_report_versions_are_explicitly_separate() -> None:
    config = tomllib.loads(_text("pyproject.toml"))
    assert config["project"]["name"] == "digibyte-quantum-adaptive-core"
    assert config["project"]["version"] == "3.1.0"
    assert config["project"]["authors"] == [{"name": "DarekDGB"}]
    assert config["project"]["dependencies"] == []
    assert _text("README.md").startswith("## DigiByte Adaptive Core (v3.1.0)\n")
    assert "**Package baseline:** v3.1.0" in _text("SECURITY.md")
    for index in ("docs/reports/INDEX.md", "docs/reports/v3/INDEX.md"):
        text = _text(index)
        assert "**Version:** v3.0.0" in text
        assert "report-document contract" in text
        assert "3.1.0" in text and "RELEASE_STATUS_V4_10_G2.md" in text
    status = " ".join(_text(STATUS).split())
    assert "899ef8efd7426ded302a1599073b950ca7e36afe" in status
    assert "13bbd054732cd22cb550b203e591c26864b685bf" in status
    assert "does not inherit Shield `v4.0.0`" in status


def test_g2_package_bump_preserves_default_export_and_integrity_locks() -> None:
    expected_hashes = {
        "tests/fixtures/adamantine/adaptive_core_adamantine_advisory_evidence_v1.json": "5b7d99ec53bfccca70b28c7bc286f388c966eb3ef33f1c1dac20b7eafac4b43d",
        "src/adaptive_core/v3/integration/adamantine.py": "95026bb7bb9e17642ec420fadfc8c72682dabc3a60d5e5ec03b37ffa6582e334",
        "src/adaptive_core/v3/envelope.py": "d46802b07d10ae3d5cb8a221fee6ac19a4935f58155937d70b484d4d64440880",
        "src/adaptive_core/v3/guardrails/amg_guardrails_v1.json": "00f717af5cd259229dc8bfe53f187703e41b543652be1bf7e22250e6a03f6ba2",
        "src/adaptive_core/v3/confidence_weights_v3.json": "6b2e3fbea9763d3e19872cea32665dda04f442b88db4eacd791ed227c9a79aef",
        "proposals/schema/upgrade_proposal_v3.schema.json": "86f0cbf11bb6168e1fbe5b81c26066c539c19234c831a942ede9afef1cdafe4a",
    }
    for relative, digest in expected_hashes.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
    assert ADAMANTINE_ADVISORY_EVIDENCE_VERSION == "adaptive_core_oracle_v3"
    default = inspect.signature(build_adamantine_advisory_evidence_v1).parameters["oracle_version"].default
    assert default == "adaptive-core/3.0.0"
    actual = build_adamantine_advisory_evidence_v1(
        context_hash="a" * 64,
        issued_at=1_760_000_000,
        expires_at=1_760_003_600,
        generated_at=1_760_000_100,
        overall_score=91,
        now=1_760_000_200,
    )
    fixture = json.loads(_text(next(iter(expected_hashes))))
    assert actual == fixture
    assert actual["oracle_version"] == default
    status = " ".join(_text(STATUS).split())
    assert "not be represented as the installed distribution's version" in status


def test_g2_public_authority_and_signature_status_claims_are_bounded() -> None:
    for relative in ("README.md", "SECURITY.md", STATUS):
        text = " ".join(_text(relative).split())
        for word in ("classical_signature", "pqc_signature", "ABSENT", "PRESENT", "UNSUPPORTED"):
            assert word in text
        assert "not signature bytes" in text
        assert "final policy and execution boundary" in text
        assert "local" in text.lower() and "artifact" in text
        assert "no live-OQS" in text
    assert "It does not verify Shield signatures" in " ".join(_text(STATUS).split())
    assert "cannot approve, override, downgrade, bypass, or rescue" in " ".join(_text("README.md").split())
    assert "never modifies state" not in _text("README.md")
    assert "never modifies state" not in _text("docs/reports/v3/README.md")


def test_g2_ci_and_counts_do_not_claim_branch_or_native_proof() -> None:
    workflow = ROOT / ".github/workflows/ci.yml"
    assert hashlib.sha256(workflow.read_bytes()).hexdigest() == "905f4ecbb2300e93ec3e9cff1e67375d25c14a9abcad7c2fec594636af695241"
    assert sorted(p.name for p in workflow.parent.iterdir()) == ["ci.yml", "demo_emit_proposal.yml"]
    assert hashlib.sha256((workflow.parent / "demo_emit_proposal.yml").read_bytes()).hexdigest() == "d1cb17f70a718a8618eda54cabdb5ae7d06ecaafb95058907539d45df5704bf2"
    config = tomllib.loads(_text("pyproject.toml"))
    assert config["tool"]["pytest"]["ini_options"]["addopts"] == "-q --cov=adaptive_core --cov-report=term-missing --cov-fail-under=100"
    for relative in (STATUS, "README.md"):
        text = " ".join(_text(relative).split())
        assert "289 passed" in text and "1505/1505" in text
    status = " ".join(_text(STATUS).split())
    assert "Branch coverage is not configured or claimed" in status
    assert "Post-commit CI and fresh-ZIP verification remain pending" in status
    assert "6 passed" in status
    integration = _text("docs/reports/v3/ADAMANTINEOS_INTEGRATION.md")
    current = integration.split("## 7. Verification", 1)[1]
    assert "289 passed." in current and "260 passed." not in current


def test_g2_release_document_links_resolve_inside_repository() -> None:
    checked = 0
    for relative in COPY_PATHS:
        if not relative.endswith(".md"):
            continue
        path = ROOT / relative
        for link in re.findall(r"\]\(([^)]+)\)", _text(relative)):
            if link.startswith(("https://", "http://", "mailto:", "#")):
                continue
            target = (path.parent / link.split("#", 1)[0]).resolve()
            target.relative_to(ROOT.resolve())
            assert target.is_file(), f"broken release link: {relative}: {link}"
            checked += 1
    assert checked >= 16


def test_g2_copy_files_are_ascii_lf_without_generated_artifact_scanning() -> None:
    for relative in COPY_PATHS:
        raw = (ROOT / relative).read_bytes()
        assert raw.isascii(), f"non-ASCII copy payload: {relative}"
        assert raw.endswith(b"\n")
        assert all(byte in (9, 10) or 32 <= byte <= 126 for byte in raw)
        for line in raw.decode("ascii").splitlines():
            assert line == line.rstrip(" \t"), f"trailing whitespace: {relative}"
